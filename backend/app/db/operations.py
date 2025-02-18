from typing import Optional, Tuple
import uuid

# import numpy as np
from sqlalchemy import func, select, Row, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import models


def get_user(db: Session, user_id: str) -> models.User | None:
    """
    Retrieve a user by their id.
    """
    query = select(models.User).filter_by(id=user_id)
    return db.scalars(query).first()


def get_user_by_email(db: Session, email: str) -> models.User | None:
    """
    Retrieve a user by their id.
    """
    query = select(models.User).filter_by(email=email)
    return db.scalars(query).first()


def create_user(db: Session, email: str, password_hash: str) -> models.User:
    db_user = models.User(
        email=email,
        hashed_password=password_hash,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def set_user_refresh_token(
    db: Session, user_id: str, refresh_token: str
) -> models.User | None:
    user = get_user(db, user_id)
    if user:
        user.refresh_token = refresh_token
        db.commit()
        return user
    return None


def get_user_library_stats(
    db: Session, user_id: str
) -> Row[Tuple[int, int]] | None:
    """Returns metadata on user's library."""
    query = (
        select(
            func.count(models.Book.id).label("n_books"),
            func.count(models.Clip.id).label("n_clips"),
        )
        .where(models.Book.user_id == user_id)
        .join(
            models.Clip,
            models.Book.id == models.Clip.document_id,
            isouter=True,
        )
    )
    return db.execute(query).first()


def get_user_library(db: Session, user_id: str):
    """Returns list of all books in user's library with metadata."""
    clips_count = (
        select(models.Book.id, func.count(models.Clip.id).label("n_clips"))
        .join(
            models.Clip,
            models.Book.id == models.Clip.document_id,
            isouter=True,
        )
        .group_by(models.Book.id)
        .subquery()
    )

    # query that joins with document with BookCatalogue to return
    query = (
        select(
            models.Book.id,
            models.Book.title,
            models.Book.authors,
            models.Book.created_at,
            models.Book.updated_at,
            func.coalesce(clips_count.c.n_clips, 0).label("n_clips"),
            func.coalesce(
                models.BookCatalogue.thumbnail_path,
                models.Book.user_thumbnail_path,
            ).label("thumbnail_path"),
            models.Book.catalogue_id,
        )
        .join(
            models.BookCatalogue,
            models.Book.catalogue_id == models.BookCatalogue.id,
            isouter=True,
        )
        .join(clips_count, models.Book.id == clips_count.c.id, isouter=True)
        .where(models.Book.user_id == user_id)
        .order_by(models.Book.created_at.desc())
    )

    return list(db.execute(query).all())


def get_user_book_by_id(
    db: Session,
    user_id: str,
    book_id: str,
) -> models.Book | None:
    """
    Get a document by its id.
    """
    query = select(models.Book).filter_by(id=book_id, user_id=user_id)
    return db.scalars(query).first()


def delete_user_book(db: Session, user_id: str, book_id: str) -> None:
    """This will delete a book and all associated clips and embeddings"""
    try:
        statement = (
            delete(models.Book)
            .where(models.Book.id == book_id)
            .where(models.Book.user_id == user_id)
        )
        db.execute(statement)
        db.commit()
    except Exception as e:
        print("Could not delete book")
        print(f"Error: {e}")
        db.rollback()
        raise e


def get_clips_by_book_id(
    db: Session, user_id: str, book_id: str
) -> list[models.Clip]:
    """Get all clips for a specific book."""
    query = (
        select(models.Clip)
        .where(models.Clip.user_id == user_id)
        .where(models.Clip.document_id == book_id)
    )
    return list(db.scalars(query).all())


def get_user_clip_by_id(
    db: Session, user_id: str, clip_id: str
) -> models.Clip | None:
    """
    Get a clip by its id.
    """
    query = (
        select(models.Clip)
        .where(models.Clip.id == clip_id)
        .where(models.Clip.user_id == user_id)
    )
    return db.scalar(query)


def get_catalogue_item_by_id(
    db: Session, catalogue_id: str
) -> models.BookCatalogue | None:
    """
    Retrieve all of a user's books.
    """
    query = select(models.BookCatalogue).filter_by(id=catalogue_id).distinct()
    return db.scalars(query).first()


def find_item_with_keyword(
    db: Session,
    user_id: str,
    keywords: str,
) -> list[models.BookCatalogue]:
    """Search title and authors for any matching keywords"""
    query = (
        select(models.BookCatalogue)
        .join(
            models.Book,
            models.Book.catalogue_id == models.BookCatalogue.id,
        )
        .where(models.Book.user_id == user_id)
        .filter(
            models.BookCatalogue.title.icontains(keywords)
            | models.BookCatalogue.authors.icontains(keywords)
        )
        .distinct()
    )
    return list(db.scalars(query).all())


def find_matching_clips(
    db: Session,
    user_id: str,
    text_hash: str,
) -> list[models.Clip]:
    """
    Find clips in the user's library that match the text hash
    """
    query = select(models.Clip).filter_by(
        user_id=user_id, content_hash=text_hash
    )
    query = query.distinct()
    return list(db.scalars(query).all())


def find_catalogue_books(
    db: Session,
    title: str,
    authors: Optional[str] = None,
) -> list[models.BookCatalogue]:
    """
    Find books in the catalogue by title and authors.

    TODO: Add fuzzy matching on title
    """
    query = select(models.BookCatalogue).filter_by(title=title)
    if authors:
        query = query.filter_by(authors=authors)

    query = query.distinct()
    return list(db.scalars(query).all())


def search_user_documents(
    db: Session,
    user_id: str,
    title: str,
    authors: Optional[str] = None,
) -> models.Book | None:
    """
    Search for a book by title and author in the user's collections
    """
    query = select(models.Book).filter_by(title=title, user_id=user_id)
    if authors:
        query = query.filter_by(authors=authors)

    query = query.distinct()
    return db.scalars(query).first()


def create_book(
    db: Session,
    user_id: str,
    title: str,
    authors: Optional[str] = None,
    user_thumbnail_path: Optional[str] = None,
    catalogue_id: Optional[str] = None,
):
    """
    Creates and inserts a new book into the database.
    """
    book = models.Book(
        title=title,
        authors=authors,
        user_id=user_id,
        user_thumbnail_path=user_thumbnail_path,
        catalogue_id=catalogue_id,
    )
    try:
        db.add(book)
        db.commit()
    except IntegrityError as e:
        print("Could not insert new book")
        print(f"Error: {e}")
        db.rollback()
    except SQLAlchemyError as e:
        print("Could not insert new book")
        print(f"Error: {e}")
        db.rollback()
    return book


def insert_clip(
    db: Session,
    clip: models.Clip,
) -> models.Clip:
    """Create a new clip for a book."""
    try:
        db.add(clip)
        db.commit()
        db.refresh(clip)
        return clip
    except Exception as e:
        print("Could not insert new clip")
        print(f"Error: {e}")
        db.rollback()
        raise e


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
    try:
        db.add(book)
        db.commit()
    except IntegrityError as e:
        print("Could not insert new catalogue item")
        print(f"Error: {e}")
        db.rollback()
    except SQLAlchemyError as e:
        print("Could not insert new catalogue item")
        print(f"Error: {e}")
        db.rollback()

    return book


def create_document(
    db: Session,
    user_id: str,
    title: str,
    authors: Optional[str] = None,
    user_thumbnail_path: Optional[str] = None,
    catalogue_id: Optional[str] = None,
) -> models.Book:
    """
    Creates a new document for the user.
    """
    try:
        book = create_book(
            db,
            user_id,
            title,
            authors,
            user_thumbnail_path,
            catalogue_id,
        )
        return book
    except Exception as e:
        print(f"Could not create document for {user_id}")
        print(f"Error: {e}")
        db.rollback()
        raise e


def insert_documents(db: Session, values: list[dict]) -> list[models.Book]:
    """Bulk insert documents and return created / existing ones."""
    if not values:
        return []

    stmt = insert(models.Book).values(values)
    stmt = stmt.on_conflict_do_update(
        constraint="unique_book",
        set_={
            "updated_at": func.now(),
        },
    ).returning(models.Book)

    results = db.scalars(stmt).all()
    db.commit()
    return list(results)


def insert_clips(
    db: Session,
    values: list[dict],
) -> list[models.Clip]:
    """
    Inserts all documents into the database.
    Return the whole row of the database for the documents.

    Clips already contains data about the document and the user. Assumes
    those parent rows are already in the database.

    Returns the new items inserted.
    """
    if not values:
        return []

    stmt = insert(models.Clip).values(values)
    stmt = stmt.on_conflict_do_nothing(
        constraint="unique_clip",
    ).returning(models.Clip)
    results = db.scalars(stmt).all()
    db.commit()
    return list(results)


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


def get_user_annotations_for_catalogue_item(
    db: Session,
    user_id: str,
    catalogue_id: str,
) -> list[models.Book]:
    """
    Get all documents belonging to a catalogue item
    """
    query = select(models.Book).filter_by(catalogue_id=catalogue_id)
    return list(db.scalars(query).all())


def get_all_user_documents(db: Session, user_id: str) -> list[models.Book]:
    """
    Returns all document associated with user.
    """
    query = select(models.Book).filter_by(user_id=user_id)
    return list(db.scalars(query).all())


def get_document_chunks(
    db: Session, document_id: str
) -> list[models.Embedding]:
    """
    Get all chunks and embeddings associated with a document.
    """
    query = select(models.Embedding).filter_by(source_id=document_id)
    return list(db.scalars(query).all())


def get_random_user_clips(
    db: Session,
    user_id: str,
    limit: int = 10,
) -> list[models.Clip]:
    """
    Returns a random selection of documents from the user's library up
    to the limit.
    """

    query = (
        select(models.Clip)
        .where(models.Clip.user_id == user_id)
        .order_by(func.random())
        .limit(limit)
    )
    return list(db.scalars(query).all())


def get_random_user_clips_with_book(
    db: Session,
    user_id: str,
    limit: int = 10,
) -> list[Row[Tuple[models.Clip, models.Book]]]:
    """
    Returns a random selection of documents from the user's library up
    to the limit.
    """

    query = (
        select(models.Clip, models.Book)
        .join(
            models.Book,
            models.Clip.document_id == models.Book.id,
        )
        .where(models.Clip.user_id == user_id)
        .order_by(func.random())
        .limit(limit)
    )
    return list(db.execute(query).all())


def get_user_clips(
    db: Session,
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    sort: Optional[str] = None,
    order_by: str = "desc",
) -> list[models.Clip]:
    """
    Assumes sort is a column in the Book table.
    """
    if sort:
        order = models.Clip.__table__.c[sort]
        order = order.desc() if order_by == "desc" else order.asc()
        query = (
            select(models.Clip)
            .where(models.Clip.user_id == user_id)
            .order_by(order)
            .limit(limit)
            .offset(offset)
        )
    else:
        query = (
            select(models.Clip)
            .where(models.Clip.user_id == user_id)
            .limit(limit)
            .offset(offset)
        )

    return list(db.scalars(query).all())


def get_user_clips_with_book(
    db: Session,
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    sort: Optional[str] = None,
    order_by: str = "desc",
) -> list[Row[Tuple[models.Clip, models.Book]]]:
    """
    Assumes sort is a column in the Book table.
    """
    if sort:
        order = models.Clip.__table__.c[sort]
        order = order.desc() if order_by == "desc" else order.asc()
        query = (
            select(models.Clip, models.Book)
            .join(
                models.Book,
                models.Clip.document_id == models.Book.id,
            )
            .where(models.Clip.user_id == user_id)
            .order_by(order)
            .limit(limit)
            .offset(offset)
        )
    else:
        query = (
            select(models.Clip, models.Book)
            .join(
                models.Book,
                models.Clip.document_id == models.Book.id,
            )
            .where(models.Clip.user_id == user_id)
            .limit(limit)
            .offset(offset)
        )

    return list(db.execute(query).all())


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
            models.Clip,
            models.Clip.id == models.Embedding.source_id,
        )
        .where(models.Clip.user_id == user_id)
    )

    if exclude_documents:
        query = query.where(models.Clip.id.notin_(exclude_documents))
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


def create_conversation(db: Session, user_id: str) -> models.Conversation:
    """
    Creates a new conversation for the user.
    """
    conversation = models.Conversation(user_id=user_id)
    try:
        db.add(conversation)
        db.commit()
    except IntegrityError as e:
        print("Could not create conversation")
        print(f"Error: {e}")
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        print("Could not create conversation")
        print(f"Error: {e}")
        db.rollback()
        raise e
    return conversation


def get_conversation(
    db: Session, user_id: str, conversation_id: str
) -> models.Conversation | None:
    """
    Retrieves the user's conversation.
    """
    query = select(models.Conversation).filter_by(
        id=conversation_id, user_id=user_id
    )
    return db.scalars(query).first()


def get_conversations(
    db: Session,
    user_id: str,
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    sort: Optional[str] = None,
    order_by: Optional[str] = "desc",
) -> list[models.Conversation]:
    """
    Retrieves all conversations for the user. Does not return messages
    but just metadata
    """
    if sort:
        order = models.Conversation.__table__.c[sort]
        order = order.desc() if order_by == "desc" else order.asc()
        query = (
            select(models.Conversation)
            .where(models.Conversation.user_id == user_id)
            .order_by(order)
            .offset(offset)
        )
    else:
        query = (
            select(models.Conversation)
            .where(models.Conversation.user_id == user_id)
            .offset(offset)
        )

    if limit:
        query = query.limit(limit)

    return list(db.scalars(query).all())


def get_message(
    db: Session, user_id: str, message_id: str
) -> models.Message | None:
    """
    Retrieves a message for a user
    """
    # Should join on conversation to ensure user access
    query = (
        select(models.Message)
        .join(
            models.Conversation,
            models.Message.conversation_id == models.Conversation.id,
        )
        .where(models.Message.id == message_id)
        .where(models.Conversation.user_id == user_id)
    )

    return db.scalars(query).first()


def add_message(
    db: Session,
    user_id: str,
    conversation_id: str,
    sender: str,
    content: str,
    parent_message_id: Optional[str] = None,
) -> models.Message:
    """
    Adds a message to the conversation and updates conversation metadata.
    """
    conversation = get_conversation(db, user_id, conversation_id)
    if not conversation:
        raise ValueError("Conversation does not exist")

    message = models.Message(
        conversation_id=conversation_id,
        sender=sender,
        content=content,
        parent_id=parent_message_id,
    )
    try:
        db.add(message)
        db.commit()

        # Maybe this should be a separate function
        conversation.updated_at = message.created_at
        if parent_message_id == conversation.current_leaf_message_uuid:
            conversation.current_leaf_message_uuid = message.id
            conversation.message_count += 1
        db.commit()

    except IntegrityError as e:
        print("Could not insert message")
        print(f"Error: {e}")
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        print("Could not insert message")
        print(f"Error: {e}")
        db.rollback()
        raise e

    return message


def add_conversation_name(
    db: Session,
    user_id: str,
    conversation_id: str,
    name: str,
) -> models.Conversation:
    """
    Adds a name to the conversation.
    """
    conversation = get_conversation(db, user_id, conversation_id)
    if not conversation:
        raise ValueError("Conversation does not exist")

    conversation.name = name
    try:
        db.commit()
    except IntegrityError as e:
        print("Could not insert message")
        print(f"Error: {e}")
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        print("Could not insert message")
        print(f"Error: {e}")
        db.rollback()
        raise e

    return conversation


def delete_conversation(
    db: Session,
    user_id: str,
    conversation_id: str,
) -> None:
    """
    Deletes a conversation and all associated messages.
    """
    try:
        statement = (
            delete(models.Conversation)
            .where(models.Conversation.id == conversation_id)
            .where(models.Conversation.user_id == user_id)
        )
        db.execute(statement)
        db.commit()
    except Exception as e:
        print("Could not delete conversation")
        print(f"Error: {e}")
        db.rollback()
        raise e


def update_clip_content(
    db: Session, user_id: str, clip_id: str, content: str
) -> models.Clip:
    """
    Updates the content of a clip. The original content remains
    in original_content_field.

    TODO: New embeddings need to be generated. Let's assume for now that
    the edits are minor and do not affect the overall meaning of the text.
    """
    clip = get_user_clip_by_id(db, user_id, clip_id)
    if not clip:
        raise ValueError("Clip does not exist")

    clip.content = content
    try:
        db.commit()
        return clip
    except Exception as e:
        print("Could not update clip content")
        print(f"Error: {e}")
        db.rollback()
        raise e


def delete_clip(
    db: Session,
    user_id: str,
    clip_id: str,
) -> None:
    """
    Deletes a conversation and all associated messages.

    Embeddings should also be deleted via cascade.
    """
    try:
        statement = (
            delete(models.Clip)
            .where(models.Clip.id == clip_id)
            .where(models.Clip.user_id == user_id)
        )
        db.execute(statement)
        db.commit()
    except Exception as e:
        print("Could not delete conversation")
        print(f"Error: {e}")
        db.rollback()
        raise e
