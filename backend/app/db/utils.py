from uuid import UUID

from app import schemas
from app.db import models
from app.utils import hash_content


def convert_book_annotation_to_db_clip(
    annotation: schemas.BookAnnotation,
    user_id: str,
    document_id: str,
) -> models.Clip:
    """
    Convert a annotation annotation for a user to a database model object.

    If a reference annotation is given, it will be used to populate the
    document
    """
    item = models.Clip(
        user_id=UUID(user_id),
        document_id=UUID(document_id),
        created_at=annotation.date_annotated,
        updated_at=None,
        original_content=annotation.content,
        content=annotation.content,
        content_hash=hash_content(annotation.content),
        location_type=annotation.location_type,
        clip_start=annotation.location_start,
        clip_end=annotation.location_end,
    )

    return item
