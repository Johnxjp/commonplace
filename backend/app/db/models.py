# This file contains database models for the backend.
import uuid
from datetime import datetime

# See pgvector.sqlalchemy support
# https://github.com/pgvector/pgvector-python?tab=readme-ov-file#sqlalchemy
from pgvector.sqlalchemy import Vector

# See https://fastapi-utils.davidmontague.xyz/user-guide/basics/guid-type/
from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.config import EMBEDDING_DIMENSIONS


class Base(DeclarativeBase):
    pass


class User(Base):
    # TODO: Consider using firebase to handle user authentication

    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        unique=True,
        nullable=False,
        server_default=text("uuid_generate_v4()"),
    )
    email: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    last_logged_in: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    refresh_token: Mapped[str | None] = mapped_column(String, nullable=True)


class Book(Base):
    """
    Table to store parent book information.
    """

    __tablename__ = "book"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        unique=True,
        nullable=False,
        server_default=text("uuid_generate_v4()"),
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    authors: Mapped[str] = mapped_column(String, nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("user.id", ondelete="cascade"), nullable=False
    )
    user_thumbnail_path: Mapped[str] = mapped_column(String, nullable=True)

    catalogue_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("book_catalogue.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, default=func.now()
    )
    clips: Mapped[list["Clip"]] = relationship(back_populates="document")

    # accessed_at: Mapped[datetime] = mapped_column(
    #     DateTime(timezone=True), nullable=True
    # )

    UniqueConstraint(user_id, title, authors, name="unique_book")

    # create the repr
    def __repr__(self) -> str:
        cols = ", ".join(
            [
                f"{k}={v}"
                for k, v in self.__dict__.items()
                if k != "_sa_instance_state"
            ]
        )
        return f"{self.__class__.__name__}({cols})"


class BookCatalogue(Base):
    """
    Reference table to store information about books. For use in things
    like disambiguation.
    """

    __tablename__ = "book_catalogue"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        unique=True,
        nullable=False,
        server_default=text("uuid_generate_v4()"),
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    authors: Mapped[str] = mapped_column(String, nullable=True)
    thumbnail_path: Mapped[str] = mapped_column(String, nullable=True)
    goodreads_url: Mapped[str] = mapped_column(String, nullable=True)
    amazon_url: Mapped[str] = mapped_column(String, nullable=True)

    # Had to be attributes and not strings
    unique_title_authors = UniqueConstraint(
        title, authors, postgresql_nulls_not_distinct=True
    )

    # create the repr
    def __repr__(self) -> str:
        cols = ", ".join(
            [
                f"{k}={v}"
                for k, v in self.__dict__.items()
                if k != "_sa_instance_state"
            ]
        )
        return f"{self.__class__.__name__}({cols})"


class Clip(Base):
    """
    Table for storing clips from a parent document
    """

    __tablename__ = "clip"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        unique=True,
        nullable=False,
        server_default=text("uuid_generate_v4()"),
    )

    # TODO: Import source. Could be an ID to import history,

    # Base document information
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("user.id", ondelete="cascade")
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("book.id", ondelete="cascade")
    )

    # When the clip was annotated
    # clipped_at: Mapped[datetime] = mapped_column(
    #     DateTime(timezone=True), nullable=True
    # )

    # When the clip was inserted
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, default=func.now()
    )

    # original_content: Mapped[str] = mapped_column(String, nullable=False)
    # original content hash
    content_hash: Mapped[str] = mapped_column(String(32), nullable=False)

    content: Mapped[str] = mapped_column(String, nullable=False)
    # clip specified as location or page depending on type
    # This can be used to add comments or marginalia to this table too
    location_type: Mapped[str] = mapped_column(String, nullable=True)
    clip_start: Mapped[int] = mapped_column(Integer, nullable=True)
    clip_end: Mapped[int] = mapped_column(Integer, nullable=True)

    # is_favourite: Mapped[bool] = mapped_column(
    #     Integer, nullable=False, default=0
    # )

    document: Mapped["Book"] = relationship(back_populates="clips")

    UniqueConstraint(user_id, document_id, content_hash, name="unique_clip")

    # create the repr
    def __repr__(self) -> str:
        cols = ", ".join(
            [
                f"{k}={v}"
                for k, v in self.__dict__.items()
                if k != "_sa_instance_state"
            ]
        )
        return f"{self.__class__.__name__}({cols})"


class Comment(Base):
    """
    Table for storing comments on documents.

    Comments are not embedded.
    """

    __tablename__ = "comment"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        unique=True,
        nullable=False,
        server_default=text("uuid_generate_v4()"),
    )

    # What comment is attached to. Can be a comment or a document.
    # If parent is deleted, delete this comment.
    parent_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(String, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, default=func.now()
    )

    def __repr__(self) -> str:
        cols = ", ".join(
            [
                f"{k}={v}"
                for k, v in self.__dict__.items()
                if k != "_sa_instance_state"
            ]
        )
        return f"{self.__class__.__name__}({cols})"


class Embedding(Base):

    __tablename__ = "document_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        nullable=False,
        unique=True,
        server_default=text("uuid_generate_v4()"),
    )

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("clip.id", ondelete="CASCADE"), nullable=False
    )

    chunk_content: Mapped[str] = mapped_column(String, nullable=False)
    cleaned_chunk: Mapped[str] = mapped_column(String, nullable=True)
    chunking_strategy: Mapped[str] = mapped_column(String, nullable=True)
    embedding = mapped_column(Vector(EMBEDDING_DIMENSIONS), nullable=False)

    # Assuming you have same embedder for all embeddings
    UniqueConstraint(source_id, chunk_content, name="unique_embedding")

    def __repr__(self) -> str:
        cols = ", ".join(
            [
                f"{k}={v}"
                for k, v in self.__dict__.items()
                if k != "_sa_instance_state"
            ]
        )
        return f"{self.__class__.__name__}({cols})"


class Conversation(Base):

    __tablename__ = "conversation"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        nullable=False,
        unique=True,
        server_default=text("uuid_generate_v4()"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )

    summary: Mapped[str] = mapped_column(String, nullable=True)

    # Which language model is used to answer the question. Configuration
    model: Mapped[str] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    # Updated At should be equal to created at in the beginning
    # Behaviour is different from above. Change others later
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    name: Mapped[str] = mapped_column(String, nullable=True)

    message_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

    # TODO: change to ID
    current_leaf_message_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID, nullable=True
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation"
    )

    def __repr__(self) -> str:
        cols = ", ".join(
            [
                f"{k}={v}"
                for k, v in self.__dict__.items()
                if k != "_sa_instance_state"
            ]
        )
        return f"{self.__class__.__name__}({cols})"


class Message(Base):

    __tablename__ = "message"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        nullable=False,
        unique=True,
        server_default=text("uuid_generate_v4()"),
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("conversation.id", ondelete="CASCADE"), nullable=False
    )

    # Every message has a parent message. If it's the first message then null
    # A parent message can have multiple
    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("message.id", ondelete="CASCADE"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), index=True
    )

    # 'system' or 'user' message
    sender: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)

    conversation: Mapped["Conversation"] = relationship(
        back_populates="messages"
    )

    def __repr__(self) -> str:
        cols = ", ".join(
            [
                f"{k}={v}"
                for k, v in self.__dict__.items()
                if k != "_sa_instance_state"
            ]
        )
        return f"{self.__class__.__name__}({cols})"
