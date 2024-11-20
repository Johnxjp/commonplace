from typing import Optional
from uuid import UUID

from app import schemas
from app.db import models
from app.utils import hash_content


def convert_book_annotation_to_db_document(
    book: schemas.BookAnnotation,
    user_id: str,
    catalogue_item: Optional[models.BookCatalogue] = None,
) -> models.Document:
    """
    Convert a book annotation for a user to a database model object.

    If a reference book is given, it will be used to populate the document
    """
    item = models.Document(
        user_id=UUID(user_id),
        title=book.title,
        authors=book.authors,
        document_type=schemas.DocumentType.BOOK.value,
        created_at=book.date_annotated,
        updated_at=None,
        content=book.content,
        content_hash=hash_content(book.content),
        is_clip=True,
        location_type=book.location_type,
        clip_start=book.location_start,
        clip_end=book.location_end,
    )

    if catalogue_item:
        item.catalogue_id = catalogue_item.id
        item.title = catalogue_item.title
        item.authors = catalogue_item.authors

    return item
