from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel


class BookAnnotationType(StrEnum):
    COMMENT = "comment"
    BOOKMARK = "bookmark"
    HIGHLIGHT = "highlight"


class DocumentType(StrEnum):
    BOOK = "book"
    VIDEO = "video"


class BookAnnotation(BaseModel):
    """Note from book with metadata"""

    title: str
    authors: str
    content: str
    annotation_type: BookAnnotationType
    location_type: Optional[str] = None
    location_start: Optional[int] = None
    location_end: Optional[int] = None
    date_annotated: Optional[datetime] = None
