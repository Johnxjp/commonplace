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


def insert_book_document(
    db: Session, user_id: str, book_id: str, document: schemas.BookAnnotation
) -> models.BookDocument:
    """
    Inserts an document into the database.
    Return the whole row of the database for the document.
    """
    data = models.BookDocument(
        content=document.content,
        user_id=user_id,
        book_id=book_id,
        is_clip=True,
        title=document.title,
        authors=document.authors,
        location_type=document.location_type,
        clip_start=document.location_start,
        clip_end=document.location_end,
        content_hash=hash_content(document.content),
    )
    db.add(data)
    db.commit()
    return data


def insert_book_all_documents(
    db: Session,
    user_id: str,
    book_id: str,
    documents: list[schemas.BookAnnotation],
) -> list[models.BookDocument]:
    """
    Inserts all documents into the database.
    Return the whole row of the database for the documents.

    Skips over duplicates which violate integrity constraints.
    """
    inserted_rows = []
    for doc in documents:
        try:
            r = insert_book_document(db, user_id, book_id, doc)
            inserted_rows.append(r)
        except IntegrityError as e:
            print(f"Could not insert {doc} for {book_id}")
            print(f"Error: {e}")
            db.rollback()
        except SQLAlchemyError as e:
            print(f"Could not insert {doc} for {book_id}")
            print(f"Error: {e}")
            db.rollback()

    return inserted_rows


def insert_embedding(
    db: Session,
    embedding: models.Embeddings,
) -> models.Embeddings:
    """
    Inserts an embedding into the database.
    """
    db.add(embedding)
    db.commit()
    return embedding


def insert_embeddings(
    db: Session,
    embeddings: list[models.Embeddings],
) -> list[models.Embeddings]:
    """
    Inserts embeddings into the database.
    """
    inserted_rows = []
    for emb in embeddings:
        try:
            r = insert_embedding(db, emb)
            inserted_rows.append(r)
        except IntegrityError as e:
            print(f"Could not insert {emb}")
            print(f"Error: {e}")
            db.rollback()
        except SQLAlchemyError as e:
            print(f"Could not insert {emb}")
            print(f"Error: {e}")
            db.rollback()

    return inserted_rows
