# Class for storing and manipulating Kindle notes
from datetime import datetime
import io
import re
from typing import BinaryIO, Dict, List, Optional, Tuple

from app.schemas import KindleAnnotation, KindleAnnotationType

AUTHOR_SEPARATOR = ";"


def process_kindle_file(
    file: BinaryIO,
) -> Dict[Tuple[str, str], List[KindleAnnotation]]:
    """
    Returns a dictionary with the key being a tuple of the title and authors
    and values as annotations for that book.
    """

    try:
        annotations = extract_annotations_from_buffer(file)
        grouped_annotations: Dict[Tuple[str, str], List[KindleAnnotation]] = {}
        for anno in annotations:
            key = (anno.title, AUTHOR_SEPARATOR.join(anno.authors))
            if key not in grouped_annotations:
                grouped_annotations[key] = []
            grouped_annotations[key].append(anno)
        return grouped_annotations
    except Exception as e:
        print(f"Unexpected error when processing file: {str(e)}")
        return {}


def extract_annotations_from_file(filename: str) -> List[KindleAnnotation]:
    """
    Extracts annotations from a file and returns those in order they appear
    in the file.
    """
    parsed_title = False
    parsed_metadata = False
    separator = "=========="
    annotations = []
    content = ""
    with open(filename, "r", encoding="utf-8-sig") as file:
        for line in file:
            # \ufeff is the BOM (byte order mark) character
            line = line.strip().strip("\ufeff")

            # Skip empty lines
            if not line:
                continue

            if not parsed_title:
                # Any instance when the above fails and this should remain false?
                # Is this actually needed?
                title = extract_title(line)
                authors = extract_authors(line)
                parsed_title = True

            elif not parsed_metadata:
                annotation_type = extract_annotation_type(line)
                if annotation_type is None:
                    annotation_type = KindleAnnotationType.HIGHLIGHT

                annotation_type = annotation_type.value
                page_start, page_end = extract_page(line)
                location_start, location_end = extract_location(line)
                date_annotated = extract_date(line)
                parsed_metadata = True

            # Marks the end of an annotation.
            elif line == separator:
                annotation = KindleAnnotation(
                    title=title,
                    authors=authors,
                    content=content,
                    annotation_type=annotation_type,
                    page_start=page_start,
                    page_end=page_end,
                    location_start=location_start,
                    location_end=location_end,
                    date_annotated=date_annotated,
                )

                if is_valid_annotation(annotation):
                    annotations.append(annotation)

                parsed_title = False
                parsed_metadata = False
                content = ""

            else:
                content += line

        # Last annotation
        if parsed_title and parsed_metadata and content:
            annotation = KindleAnnotation(
                title=title,
                authors=authors,
                content=content,
                annotation_type=annotation_type,
                page_start=page_start,
                page_end=page_end,
                location_start=location_start,
                location_end=location_end,
                date_annotated=date_annotated,
            )
            if is_valid_annotation(annotation):
                annotations.append(annotation)

        return annotations


def extract_annotations_from_buffer(file: BinaryIO) -> List[KindleAnnotation]:
    """
    Extracts annotations from buffer of bytes and returns those in order they
    appear in the file.

    The way clippings.io does it is to check for the existence of the
    title, author and page information. If these exist then ok.
    It will then collect the text.

    If there is a malformed section it will skip it as well as skipping empty
    lines
    """
    parsed_title = False
    parsed_metadata = False
    separator = "=========="
    annotations = []
    content = ""
    for line in io.TextIOWrapper(file, encoding="utf-8-sig"):
        # \ufeff is the BOM (byte order mark) character
        line = line.strip().strip("\ufeff")

        # Skip empty lines
        if not line:
            continue

        if not parsed_title:
            # Any instance when the above fails and this should remain false?
            # Is this actually needed?
            title = extract_title(line)
            authors = extract_authors(line)
            parsed_title = True

        elif not parsed_metadata:
            annotation_type = extract_annotation_type(line)
            if annotation_type is None:
                annotation_type = KindleAnnotationType.HIGHLIGHT

            annotation_type = annotation_type.value
            page_start, page_end = extract_page(line)
            location_start, location_end = extract_location(line)
            date_annotated = extract_date(line)
            parsed_metadata = True

        # Marks the end of an annotation.
        elif line == separator:
            annotation = KindleAnnotation(
                title=title,
                authors=authors,
                content=content,
                annotation_type=annotation_type,
                page_start=page_start,
                page_end=page_end,
                location_start=location_start,
                location_end=location_end,
                date_annotated=date_annotated,
            )

            if is_valid_annotation(annotation):
                annotations.append(annotation)

            parsed_title = False
            parsed_metadata = False
            content = ""

        else:
            content += line

    # Last annotation
    if parsed_title and parsed_metadata and content:
        annotation = KindleAnnotation(
            title=title,
            authors=authors,
            content=content,
            annotation_type=annotation_type,
            page_start=page_start,
            page_end=page_end,
            location_start=location_start,
            location_end=location_end,
            date_annotated=date_annotated,
        )
        if is_valid_annotation(annotation):
            annotations.append(annotation)

    return annotations


def is_valid_annotation(annotation: KindleAnnotation) -> bool:
    """
    Valid clips should have some content and be associated with a book.

    TODO: Validation can easily return true just by having a normal without any
    breaks as the system will just grab first line as title and the rest as
    content
    """
    # ignore clips with no content
    if len(annotation.content) == 0:
        return False

    # ignore clips with no title
    if not annotation.title:
        return False

    if annotation.annotation_type == KindleAnnotationType.BOOKMARK.value:
        return False

    return True


def extract_title(line: str) -> str:
    """
    Returns the title of the book from the line containing the title
    and author of the book.

    The title is the part of the line before the first open bracket.

    TODO: Normalise Title
    """
    open_bracket = line.find("(")
    if open_bracket == -1:
        return line

    return line[:open_bracket].strip()


def extract_authors(line: str) -> List[str]:
    """
    Returns a list of authors with each name extracted as
    `<first name> <other names>`.

    The author will be within the last set of brackets. There can be nested
    brackets which need to be handled.
    """
    stack = []
    last_opening = -1
    last_closing = -1

    for i, char in enumerate(line):
        if char == "(":
            stack.append(i)
        elif char == ")":
            if stack:
                last_opening = stack.pop()
                last_closing = i

    if last_opening == -1 or last_closing == -1 or last_closing < last_opening:
        return []

    authors_str = line[last_opening + 1 : last_closing]
    if len(authors_str):
        # Handle case with multiple authors
        # Author names are usually written as '<first name>, <last name>'
        authors = authors_str.split(AUTHOR_SEPARATOR)
        return [_swap_parts_of_name(name) for name in authors]

    return []


def extract_annotation_type(line: str) -> Optional[KindleAnnotationType]:
    """
    Extracts the type of note from the second line of a highlight.

    Returns 'None' if the type cannot be found.
    """
    if "Note" in line:
        return KindleAnnotationType.NOTE

    if "Bookmark" in line:
        return KindleAnnotationType.BOOKMARK

    if "Highlight" in line:
        return KindleAnnotationType.HIGHLIGHT

    # If unknown
    return None


def extract_page(line: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Returns the start and end page number of the annotation. If it doesn't
    exist, returns a tuple of Nones
    """
    pattern = re.compile(r"page (\d+-\d+)", re.IGNORECASE)
    match = re.search(pattern, line)
    if match:
        pages = match.group(1).split("-")
        return int(pages[0]), int(pages[1])

    pattern = re.compile(r"page (\d+)", re.IGNORECASE)
    match = re.search(pattern, line)
    if match:
        pages = match.group(1)
        return int(pages), None

    # Fallback
    pattern = re.compile(r"\d+-\d+", re.IGNORECASE)
    match = re.search(pattern, line)
    if match:
        pages = match.group().split("-")
        return int(pages[0]), int(pages[1])

    return None, None


def extract_location(line: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Returns the start and end location number of the annotation. If it doesn't
    exist, returns a tuple of Nones
    """
    pattern = re.compile(r"location (\d+-\d+)", re.IGNORECASE)
    match = re.search(pattern, line)
    if match:
        loc = match.group(1).split("-")
        return int(loc[0]), int(loc[1])

    pattern = re.compile(r"location (\d+)", re.IGNORECASE)
    match = re.search(pattern, line)
    if match:
        loc = match.group(1)
        return int(loc), None

    # Fallback
    pattern = re.compile(r"\d+-\d+", re.IGNORECASE)
    match = re.search(pattern, line)
    if match:
        loc = match.group().split("-")
        return int(loc[0]), int(loc[1])

    return None, None


def extract_date(info: str) -> Optional[int]:
    """
    Extracts the date from a highlight and return as a millisecond timestamp.

    Dates are recorded on the second line of a
    highlight in the following format:
    '- Your Highlight on page 43 | location 973-974 |
    Added on Thursday, 28 January 2016 08:33:31'
    """
    pattern = re.compile(
        r"\d{1,2}\s\w+\s\d{4}\s\d{2}:\d{2}:\d{2}", re.IGNORECASE
    )
    match = re.search(pattern, info)
    if match:
        dt = datetime.strptime(match.group(0), "%d %B %Y %H:%M:%S")
        return int(dt.timestamp() * 1000)
    return None


def _swap_parts_of_name(name: str) -> str:
    """
    Reformats the author name from `<last names>, <first name>`
    to `<first name> <last name>`

    Note: this will not handle cases like
    ("lincoln, abraham dr,", "dr, abraham lincoln") and
    ("Agriculture, urban and food hall"),
    """
    name_parts = name.split(",")
    if len(name_parts) == 1:
        return name_parts[0].strip()

    first_name = name_parts[1].strip()
    last_names = name_parts[0].strip()
    return f"{first_name} {last_names}"
