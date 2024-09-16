from enum import StrEnum
from typing import Optional

from pydantic import BaseModel


class KindleAnnotationType(StrEnum):
    NOTE = "note"
    BOOKMARK = "bookmark"
    HIGHLIGHT = "highlight"


class KindleAnnotation(BaseModel):
    """Base class for Kindle annotations"""

    title: str
    content: str = ""
    authors: list[str]
    annotation_type: str
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    location_start: Optional[int] = None
    location_end: Optional[int] = None
    date_annotated: Optional[int] = None
