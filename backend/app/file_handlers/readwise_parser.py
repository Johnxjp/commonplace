""" Parses export documents from readwise """

from datetime import datetime
import logging
from typing import Dict, Tuple

import pandas as pd

from app.config import AUTHOR_SEPARATOR
from app.schemas import (
    BookAnnotation,
    BookAnnotationType,
    BOOK_TITLE,
    BOOK_AUTHORS,
)


logger = logging.getLogger(__name__)


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


def parse_author(raw_author: str) -> str:
    """
    Parse the author string. Split multiple authors by semicolon.
    """
    if " and " in raw_author:
        return raw_author.replace(" and ", AUTHOR_SEPARATOR)
    return raw_author


def process_readwise_csv(
    filepath: str,
) -> Dict[Tuple[BOOK_TITLE, BOOK_AUTHORS], list[BookAnnotation]]:
    """
    Parse a valid readwise export file and return a list of
    annotation objects.

    Readwise csv schema:
    - Highlight: str
    - Book Title: str
    - Book Author: str
    - Amazon Book ID: str
    - Note: str | nan
    - Color: str
    - Tags: str
    - Location Type: str [page, location]
    - Location: int
    - Highlighted at: datetime
    - Document tags: str | nan
    """
    data = pd.read_csv(filepath, delimiter=",", header=0)
    grouped = data.groupby(["Book Title", "Book Author"], dropna=False)
    content = {}
    for (title, authors), rows in grouped:
        annotations = []
        print(f"Number of items for book {title} {authors}", len(rows))
        annotations_added = 0
        authors = parse_author(authors) if pd.notna(authors) else None
        for idx, row in rows.iterrows():
            try:
                location_type = row["Location Type"]
                if pd.isna(row["Location Type"]):
                    location_type = "location"

                date_annotated = datetime.fromisoformat(row["Highlighted at"])
                annotation = BookAnnotation(
                    title=title,
                    authors=authors,
                    content=row["Highlight"],
                    annotation_type=BookAnnotationType.HIGHLIGHT,
                    location_type=location_type,
                    location_start=int(row["Location"]),
                    location_end=None,
                    date_annotated=date_annotated,
                )
                annotations.append(annotation)
                annotations_added += 1

                if pd.notna(row["Note"]):
                    note = BookAnnotation(
                        title=title,
                        authors=authors,
                        content=row["Note"],
                        annotation_type=BookAnnotationType.COMMENT,
                        location_type=location_type,
                        location_start=int(row["Location"]),
                        location_end=None,
                        date_annotated=date_annotated,
                    )
                    annotations.append(note)
                    annotations_added += 1

            except Exception as e:
                print(f"Error parsing row {idx} in ({title}, {authors}): {e}")
                print(row)

        # print(f"Added {annotations_added} annotations for {title} {authors}")
        if annotations_added < len(rows):
            print(
                f"Only added {annotations_added} of {len(rows)} annotations for {title} {authors}"
            )
        # print(f"Added {annotations_added} annotations for {title} {authors}")
        content[(title, authors)] = annotations

    return content
