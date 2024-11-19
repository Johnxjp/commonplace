from uuid import UUID
from typing import Optional, Tuple


# import numpy as np
from sqlalchemy import select, Row
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app import schemas
from app.db import models
from app.index.vectoriser import embed
from app.utils import hash_content


def get_library(db: Session, user_id: str) -> list[models.BookCatalogue]:
    """
    Retrieve all of a user's books.
    """
    user_documents = (
        select(models.Document)
        .where(models.Document.user_id == user_id)
        .subquery()
    )

    query = select(models.BookCatalogue).join(
        user_documents,
        user_documents.c.catalogue_id == models.BookCatalogue.id,
    )
    return list(db.scalars(query).all())


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
) -> models.Document:
    """
    Inserts an document into the database.
    Return the whole row of the database for the document.
    """
    data = models.Document(
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
) -> list[models.Document]:
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
    embedding: models.Embedding,
) -> models.Embedding:
    """
    Inserts an embedding into the database.
    """
    db.add(embedding)
    db.commit()
    return embedding


def insert_embeddings(
    db: Session,
    embeddings: list[models.Embedding],
) -> list[models.Embedding]:
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


def get_document_by_id(
    db: Session,
    document_id: str,
    user_id: str,
) -> models.Document | None:
    """
    Get a document by its id.
    """
    query = select(models.Document).filter_by(id=document_id, user_id=user_id)
    result = db.scalars(query).first()
    return result


def get_user_document_ids(db: Session, user_id: str) -> list[UUID]:
    """
    Get all documents associated with user across books and videos.
    """
    query = select(models.Document.id).filter_by(user_id=user_id)
    result = db.execute(query).all()
    return [r.id for r in result]


def get_documents(db: Session, limit: Optional[int] = 10, random: bool = True):
    pass


# def get_similar_chunks(
#     db: Session, user_id: str, text: str, topk: int = 5
# ) -> list[Row[Tuple[models.Embeddings, float]]]:
#     """
#     Retrieve similar chunks to a user's text by performing a cosine similarity
#     search across embeddings belonging to the user. Returns the topk results.

#     Args:
#         db: SQLAlchemy session
#         user_id: User id
#         text: Text to search for
#         topk: Number of results to return

#     Returns: list of tuples containing ids of similar chunks from Embedding
#     table and their cosine similarity scores, ordered by highest to lowest
#     score.
#     """

#     user_embeddings_subquery = _join_embeddings_with_user_sources(
#         db, user_id
#     ).cte("user_embeddings")

#     query = (
#         select(
#             user_embeddings_subquery.c.source_id,
#             user_embeddings_subquery.c.embedding.cosine_distance(
#                 embed(text)
#             ).label("score"),
#         )
#         .order_by("score")
#         .limit(topk)
#     )

#     results = db.execute(query).all()
#     return list(results)
