""" Parses export documents from readwise """

from datetime import datetime

import pandas as pd

from app import schemas


def validate_readwise_csv(filepath: str) -> bool:
    """
    Just check for existence of column names in the header
    Should really check for the type of the columns as well
    """
    contents = pd.read_csv(filepath, delimiter=",", header=0)
    header = contents.columns.tolist()
    if header != [
        "Highlight",
        "Book Title",
        "Book Author",
        "Amazon Book ID",
        "Note",
        "Color",
        "Tags",
        "Location Type",
        "Location",
        "Highlighted at",
        "Document tags",
    ]:
        return False

    return True


def process_readwise_csv(filepath: str) -> list[schemas.BookAnnotation]:
    """
    Parse a valid readwise export file and return a list of
    annotation objects.

    Readwise csv schema:
    - Highlight: str
    - Book Title: str
    - Book Author: str
    - Amazon Book ID: str
    - Note: str
    - Color: str
    - Tags: str
    - Location Type: str [page, location]
    - Location: int
    - Highlighted at: datetime
    - Document tags: str
    """
    content = []
    data = pd.read_csv(filepath, delimiter=",", header=0)
    for row_num, row in data.iterrows():
        try:
            date_annotated = datetime.fromisoformat(row["Highlighted at"])
            annotation = schemas.BookAnnotation(
                title=row["Book Title"],
                authors=row["Book Author"],
                content=row["Highlight"],
                annotation_type=schemas.BookAnnotationType.HIGHLIGHT,
                location_type=row["Location Type"],
                location_start=int(row["Location"]),
                location_end=None,
                date_annotated=date_annotated,
            )
            content.append(annotation)

            if row["Note"]:
                note = schemas.BookAnnotation(
                    title=row["Book Title"],
                    authors=row["Book Author"],
                    content=row["Note"],
                    annotation_type=schemas.BookAnnotationType.COMMENT,
                    location_type=row["Location Type"],
                    location_start=int(row["Location"]),
                    location_end=None,
                    date_annotated=date_annotated,
                )
                content.append(note)

        except Exception as e:
            print(f"Error parsing row {row_num}: {e}")

    return content
