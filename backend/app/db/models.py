# This file contains database models for the backend.
import uuid
from datetime import datetime

# See pgvector.sqlalchemy support
# https://github.com/pgvector/pgvector-python?tab=readme-ov-file#sqlalchemy
from pgvector.sqlalchemy import Vector

# See https://fastapi-utils.davidmontague.xyz/user-guide/basics/guid-type/
from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Boolean,
    DateTime,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

from app.config import EMBEDDING_DIMENSIONS


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        unique=True,
        nullable=False,
        server_default=text("uuid_generate_v4()"),
    )
    # email: Mapped[str] = mapped_column(String, nullable=False)
    # firebase_id: Mapped[str] = mapped_column(
    #     String, unique=True, nullable=False
    # )  # TODO: Create firebase
    # username: Mapped[str] = mapped_column(String, nullable=True)
    # disabled: Mapped[bool] = mapped_column(
    #     Boolean, nullable=False, default=False
    # )
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    # last_logged_in: Mapped[str] = mapped_column(
    #     DateTime(timezone=True), nullable=True
    # )


# subscription = relationship("Subscription", back_populates="user")


class BookCatalogue(Base):
    """Reference table to store information about books. For use in things
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

    # Had to be attributes and not strings
    unique_title_authors = UniqueConstraint(title, authors)

    def __repr__(self) -> str:
        return (
            f"Book(id={self.id}, "
            f"title={self.title}, "
            f"authors={self.authors}, "
            f"thumbnail_path={self.thumbnail_path})"
        )


class BookDocument(Base):
    """Single table that contains all documents and their clips"""

    __tablename__ = "book_document"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        unique=True,
        nullable=False,
        server_default=text("uuid_generate_v4()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("user.id", ondelete="cascade")
    )
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("book_catalogue.id")
    )

    title: Mapped[str] = mapped_column(String, nullable=False)
    authors: Mapped[str] = mapped_column(String, nullable=True)

    # clip specified as location or page depending on type
    is_clip: Mapped[str] = mapped_column(Boolean, nullable=False)
    location_type: Mapped[str] = mapped_column(String, nullable=True)
    clip_start: Mapped[int] = mapped_column(Integer, nullable=True)
    clip_end: Mapped[int] = mapped_column(Integer, nullable=True)

    # text from book
    content: Mapped[str] = mapped_column(String, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(32), nullable=False)

    # Clips can be created separately from the book
    # BookDocument entirely should be same as Document row
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    UniqueConstraint(book_id, content_hash, name="unique_book_clip")

    # create the repr
    def __repr__(self) -> str:
        return (
            f"BookDocument("
            f"id={self.id},"
            f"title={self.title},"
            f"authors={self.authors},"
            f"user_id={self.user_id},"
            f"book_id={self.user_id},"
            f"content={self.content},"
            f"is_clip={self.is_clip}"
            f"clip_start={self.clip_start},"
            f"clip_end={self.clip_end},"
            f"location_type={self.location_type},"
            f"created_at={self.created_at},"
            ")"
        )


class VideoDocument(Base):
    """Single table that contains all video documents and their clips"""

    __tablename__ = "video_document"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        unique=True,
        nullable=False,
        server_default=text("uuid_generate_v4()"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("user.id", ondelete="cascade")
    )

    # source url — youtube videos. Base URL without query params
    source_url: Mapped[str] = mapped_column(String, nullable=False)

    title: Mapped[str] = mapped_column(String, nullable=False)

    # channel for youtube
    authors: Mapped[str] = mapped_column(String, nullable=True)

    # Store as seconds
    clip_start: Mapped[int] = mapped_column(Integer, nullable=True)
    clip_end: Mapped[int] = mapped_column(Integer, nullable=True)
    is_clip: Mapped[str] = mapped_column(Boolean, nullable=False)

    # transcript
    content: Mapped[str] = mapped_column(String, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    UniqueConstraint(source_url, clip_start, clip_end, name="unique_video")

    # create the repr
    def __repr__(self) -> str:
        return (
            f"VideoDocument("
            f"id={self.id},"
            f"title={self.title},"
            f"authors={self.authors},"
            f"source_url={self.source_url},"
            f"user_id={self.user_id},"
            f"content={self.content},"
            f"is_clip={self.is_clip}"
            f"clip_start={self.clip_start},"
            f"clip_end={self.clip_end},"
            ")"
        )


class Embeddings(Base):
    """
    Can enrich embeddings with a number of different metadata
    e.g. keywords.
    """

    __tablename__ = "document_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        nullable=False,
        unique=True,
        server_default=text("uuid_generate_v4()"),
    )

    # source of chunk
    source_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False)

    # chunk_content
    chunk_content: Mapped[str] = mapped_column(String, nullable=False)
    cleaned_chunk: Mapped[str] = mapped_column(String, nullable=True)
    chunking_strategy: Mapped[str] = mapped_column(String, nullable=True)
    embedding = mapped_column(Vector(EMBEDDING_DIMENSIONS), nullable=False)

    # Assuming you have same embedder for all embeddings
    UniqueConstraint(source_id, chunk_content, name="unique_embedding")

    def __repr__(self) -> str:
        return (
            f"Embeddings("
            f"id={self.id},"
            f"source_id={self.source_id},"
            f"chunk_content={self.chunk_content},"
            f"cleaned_chunk={self.cleaned_chunk},"
            f"chunking_strategy={self.chunking_strategy},"
            ")"
        )
