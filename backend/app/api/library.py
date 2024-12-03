"""
Endpoints related to documents:

1. Retrieve all of a user's documents
2. Retrieve all of a user's container documents
3. Retrieve a document by id
4. Retrieve similar documents to a given document
5. Retrieve similar documents to a given text
6. Retrieve a selection of user's documents

TODO: How to do this by user?

"""

from uuid import UUID

from datetime import datetime
import logging
from typing import Optional

# from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api.utils import get_current_user
from app.db import get_db, operations, models
from app.index import retrieval

logger = logging.getLogger(__name__)


LibraryRouter = APIRouter()


class LibraryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    authors: str | None
    created_at: datetime
    updated_at: datetime | None
    n_clips: int
    thumbnail_path: str | None
    catalogue_id: UUID | None


@LibraryRouter.get("/library")
def get_user_library(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[LibraryItem]:
    """
    This will return a list of all documents in the user's library
    including metadata about the document.
    """
    try:
        items = [
            LibraryItem.model_validate(item)
            for item in operations.get_user_library(db, user_id)
        ]
        return items
    except Exception as e:
        logger.error(f"Error getting user library: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error getting user library.",
        )


@LibraryRouter.get("/documents/{document_id}/annotations")
def get_user_document_annotations(
    document_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns user annotations and metadata about the book"""
    book = operations.get_user_book_by_id(db, user_id, document_id)
    if not book:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Book with {document_id=} belonging to {user_id=} not found."
            ),
        )

    annotations = operations.get_clips_by_book_id(db, user_id, document_id)
    return {
        "annotations": annotations,
        "total": len(annotations),
        "source": book,
    }


@LibraryRouter.get("/clip/{clip_id}")
def get_user_clip(
    clip_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a clip by its id. Return with book information
    """
    # No unified source table so need to check all document source tables
    clip = operations.get_user_clip_by_id(
        db,
        user_id,
        clip_id,
    )
    # Join with document to get book information
    if not clip:
        raise HTTPException(
            status_code=404,
            detail=f"Clip with {id=} belonging to {user_id=} not found.",
        )
    return {}


@LibraryRouter.get("/documents/{document_id}")
def get_user_document(
    document_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a document by its id. A document can be a book or a video and therefore
    need to check both sources.
    """

    # No unified source table so need to check all document source tables
    document = operations.get_user_book_by_id(
        db,
        user_id,
        document_id,
    )
    if not document:
        return HTTPException(
            status_code=404,
            detail=f"Document with {id=} belonging to {user_id=} not found.",
        )
    return document


@LibraryRouter.get("/documents")
def get_documents(
    limit: int = 10,
    offset: int = 0,
    sort: Optional[str] = None,
    order_by: Optional[str] = "desc",
    random: bool = False,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all documents in the database.
    """
    if random:
        return operations.get_random_user_clips(
            db, user_id=user_id, limit=limit
        )

    table_columns = models.Book.__table__.columns.keys()
    if sort and sort not in table_columns:
        return HTTPException(
            status_code=400,
            detail=(
                f"Invalid sort field '{sort}' for {models.Book.__name__}."
            ),
        )

    if order_by not in ["asc", "desc"]:
        print(f"Invalid {order_by=} value. Setting to default of 'desc'.")
        order_by = "desc"

    return operations.get_user_clips(
        db,
        user_id=user_id,
        limit=limit,
        offset=offset,
        sort=sort,
        order_by=order_by,
    )


@LibraryRouter.get("/clips/{clip_id}/similar")
def get_similar_clips(
    clip_id: str,
    topk: int = 5,
    threshold: float = 0.5,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get semantically similar documents to a given document based on the
    content and return up to topk similar documents.
    """
    if not operations.get_user_clip_by_id(db, user_id, clip_id):
        return HTTPException(
            status_code=404,
            detail=(
                f"Clip with {clip_id=} " f"belonging to {user_id=} not found.",
            ),
        )

    similar_document_ids = retrieval.get_similar_user_clips(
        db, user_id, clip_id, topk=topk
    )

    output = []
    for clip_id, score in similar_document_ids:
        document = operations.get_user_clip_by_id(db, user_id, clip_id)
        if not document:
            logger.error(f"Document with id {clip_id} not found in database.")
            continue

        book = operations.get_user_book_by_id(
            db, user_id, str(document.document_id)
        )

        if not book:
            logger.error(
                f"No book with id {document.document_id} associated "
                f"with clip {clip_id}."
            )
            continue

        output.append(
            {
                "id": document.id,
                "title": book.title,
                "authors": book.authors,
                "created_at": document.created_at,
                "updated_at": document.updated_at,
                "content": document.content,
                "is_clip": True,
                "location_type": document.location_type,
                "clip_start": document.clip_start,
                "clip_end": document.clip_end,
                "catalogue_id": book.catalogue_id,
                "score": score,
            }
        )
    return output


@LibraryRouter.post("/answer")
def answer_user_query(
    query: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Recognises the intent of the user's query and returns the appropriate
    response based on knowledge in the user's library.

    This function requires:
    1. Decomposing the user's query to recognise intent and to structure
    the query in a form the system can understand.
    2. Searching for an answer based on the intent
    3. Providing the retrieved output to a language model to generate a
    response.
    4. Saving the search history for the user.
    5. Returning the response to the user.
    """
    pass


@LibraryRouter.post("/library/search")
def library_search(
    query: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Searches the library for any exact matches on either the title or author.
    Returns items based on match.
    """
    return operations.find_item_with_keyword(db, user_id, query)
