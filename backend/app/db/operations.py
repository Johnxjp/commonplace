from typing import Optional, Tuple


# import numpy as np
from sqlalchemy import func, select, Row
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app import schemas
from app.db import models
from app.utils import hash_content


def get_user_library(db: Session, user_id: str) -> list[models.BookCatalogue]:
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
    user_id: str,
    document_id: str,
) -> models.Document | None:
    """
    Get a document by its id.
    """
    query = select(models.Document).filter_by(id=document_id, user_id=user_id)
    return db.scalars(query).first()


def get_all_user_documents(db: Session, user_id: str) -> list[models.Document]:
    """
    Returns all document associated with user.
    """
    query = select(models.Document).filter_by(user_id=user_id)
    return list(db.scalars(query).all())


def get_document_chunks(
    db: Session, document_id: str
) -> list[models.Embedding]:
    """
    Get all chunks and embeddings associated with a document.
    """
    query = select(models.Embedding).filter_by(source_id=document_id)
    return list(db.scalars(query).all())


def get_random_user_documents(
    db: Session,
    user_id: str,
    limit: int = 10,
    random_seed: Optional[int] = None,
) -> list[models.Document]:
    """
    Returns a random selection of documents from the user's library up
    to the limit.
    """

    query = (
        select(models.Document)
        .where(models.Document.user_id == user_id)
        .order_by(func.random())
        .limit(limit)
    )
    return list(db.scalars(query).all())


def get_user_documents(
    db: Session,
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    sort: Optional[str] = None,
    order_by: str = "desc",
) -> list[models.Document]:
    """
    Assumes sort is a column in the Document table.
    """
    if sort:
        order = models.Document.__table__.c[sort]
        order = order.desc() if order_by == "desc" else order.asc()
        query = (
            select(models.Document)
            .where(models.Document.user_id == user_id)
            .order_by(order)
            .limit(limit)
            .offset(offset)
        )
    else:
        query = (
            select(models.Document)
            .where(models.Document.user_id == user_id)
            .limit(limit)
            .offset(offset)
        )

    return list(db.scalars(query).all())


def get_similar_chunks(
    db: Session,
    user_id: str,
    query_embedding: list[float],
    topk: int = 5,
    exclude_documents: list[str] | None = None,
    exclude_chunks: list[str] | None = None,
) -> list[Row[Tuple[models.Embedding, float]]]:
    """
    Retrieve similar chunks to a user's text by performing a cosine similarity
    search across embeddings belonging to the user. Returns the topk results.

    Returns: list of tuples containing ids of similar chunks from Embedding
    table and their cosine similarity scores, ordered by highest to lowest
    score.
    """
    query = (
        select(models.Embedding)
        .join(
            models.Document,
            models.Document.id == models.Embedding.source_id,
        )
        .where(models.Document.user_id == user_id)
    )

    if exclude_documents:
        query = query.where(models.Document.id.notin_(exclude_documents))
    if exclude_chunks:
        query = query.where(models.Embedding.id.notin_(exclude_chunks))

    query = query.subquery()
    query = (
        select(
            query,
            query.c.embedding.cosine_distance(query_embedding).label("score"),
        )
        .order_by("score")
        .limit(topk)
    )
    return list(db.execute(query).all())
