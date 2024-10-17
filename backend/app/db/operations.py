from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app import schemas
from app.db import models
from app.utils import hash_content


# def get_thumbnail_path(title: str, author: str) -> Optional[str]:
#     return None


def search_book_by_metadata(
    db: Session,
    title: str,
    authors: Optional[str] = None,
) -> list[models.BookCatalogue]:
    """
    Search for a book by title and author in the database.
    Returns a list of books that match.
    """
    results = db.scalars(
        select(models.BookCatalogue).filter_by(title=title)
    ).all()

    if authors:
        return list(filter(lambda x: x.authors == authors, results))

    return list(results)


def create_book_catalogue_item(
    db: Session,
    title: str,
    authors: Optional[str] = None,
    thumbnail_path: Optional[str] = None,
) -> models.BookCatalogue:
    """
    Creates and inserts a new book into the database.
    """

    book = models.BookCatalogue(
        title=title,
        authors=authors,
        thumbnail_path=thumbnail_path,
    )
    db.add(book)
    db.commit()
    return book


def insert_book_annotation(
    db: Session, user_id: str, book_id: str, annotation: schemas.BookAnnotation
) -> models.BookDocument:
    """
    Inserts an annotation into the database.
    Return the whole row of the database for the annotation.
    """
    document = models.BookDocument(
        content=annotation.content,
        user_id=user_id,
        book_id=book_id,
        is_clip=True,
        title=annotation.title,
        authors=annotation.authors,
        location_type=annotation.location_type,
        clip_start=annotation.location_start,
        clip_end=annotation.location_end,
        content_hash=hash_content(annotation.content),
    )
    db.add(document)
    db.commit()
    return document


def insert_book_all_annotations(
    db: Session,
    user_id: str,
    book_id: str,
    annotations: list[schemas.BookAnnotation],
) -> list[models.BookDocument]:
    """
    Inserts all annotations into the database.
    Return the whole row of the database for the annotations.
    """
    inserted_rows = []
    for ann in annotations:
        try:
            r = insert_book_annotation(db, user_id, book_id, ann)
            inserted_rows.append(r)
        except IntegrityError as e:
            print("Could not insert {ann} for {book_id}")
            print(f"Error: {e}")
            db.rollback()
        except SQLAlchemyError as e:
            print("Could not insert {ann} for {book_id}")
            print(f"Error: {e}")
            db.rollback()

    return inserted_rows
