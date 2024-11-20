from typing import Optional


# import numpy as np
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app import schemas
from app.db import models
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

    query = (
        select(models.BookCatalogue)
        .join(
            user_documents,
            user_documents.c.catalogue_id == models.BookCatalogue.id,
        )
        .distinct()
    )
    return list(db.scalars(query).all())


def search_library_by_query(
    db: Session,
    user_id: str,
    text: str,
) -> list[models.BookCatalogue]:
    """Search title and authors for any matching keywords"""
    user_documents = (
        select(models.Document)
        .where(models.Document.user_id == user_id)
        .subquery()
    )

    query = (
        select(models.BookCatalogue)
        .join(
            user_documents,
            user_documents.c.catalogue_id == models.BookCatalogue.id,
        )
        .filter(
            models.BookCatalogue.title.icontains(text)
            | models.BookCatalogue.authors.icontains(text)
        )
        .distinct()
    )
    return list(db.scalars(query).all())


def search_book_by_author(
    db: Session,
    user_id: str,
    authors: str,
) -> list[models.BookCatalogue]:
    """
    Search for a book by author in the database.
    Returns a list of books that match.
    """
    user_documents = (
        select(models.Document)
        .where(models.Document.user_id == user_id)
        .subquery()
    )

    query = (
        select(models.BookCatalogue)
        .join(
            user_documents,
            user_documents.c.catalogue_id == models.BookCatalogue.id,
        )
        .filter_by(authors=authors)
        .distinct()
    )
    return list(db.scalars(query).all())


def find_matching_documents(
    db: Session,
    user_id: str,
    text_hash: str,
    title: Optional[str] = None,
    authors: Optional[str] = None,
) -> list[models.Document]:
    """
    Find documents in the user's library that match the text.
    """
    user_documents = (
        select(models.Document)
        .where(models.Document.user_id == user_id)
        .subquery()
    )

    query = (
        select(models.Document)
        .join(
            user_documents,
            user_documents.c.id == models.Document.id,
        )
        .filter_by(content_hash=text_hash)
    )
    if title:
        query = query.filter_by(title=title)
    if authors:
        query = query.filter_by(authors=authors)

    query = query.distinct()
    return list(db.scalars(query).all())


def find_books_in_catalogue(
    db: Session,
    title: str,
    authors: Optional[str] = None,
) -> list[models.BookCatalogue]:
    """
    Find books in the catalogue by title and authors.

    TODO: Add author filters
    TODO: Add fuzzy matching on title
    """
    query = select(models.BookCatalogue).filter_by(title=title).distinct()
    return list(db.scalars(query).all())


def search_user_books(
    db: Session,
    user_id: str,
    title: str,
    authors: Optional[str] = None,
) -> list[models.BookCatalogue]:
    """
    Search for a book by title and author in the user's collections

    TODO: Requires fuzzy matching
    """
    user_documents = (
        select(models.Document)
        .where(models.Document.user_id == user_id)
        .subquery()
    )

    query = (
        select(models.BookCatalogue)
        .join(
            user_documents,
            user_documents.c.catalogue_id == models.BookCatalogue.id,
        )
        .filter_by(title=title)
        .distinct()
    )
    return list(db.scalars(query).all())


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


def get_user_document_by_id(
    db: Session,
    document_id: str,
    user_id: str,
) -> models.Document | None:
    """
    Get a document by its id.
    """
    query = select(models.Document).filter_by(id=document_id, user_id=user_id)
    return db.scalars(query).first()


def get_user_documents(db: Session, user_id: str) -> list[models.Document]:
    """
    Returns all document associated with user.
    """
    query = select(models.Document).filter_by(user_id=user_id)
    return list(db.scalars(query).all())


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
