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

import logging
from typing import Optional

# from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.utils import get_current_user
from app.db import get_db, operations, models
from app.index import retrieval

logger = logging.getLogger(__name__)


LibraryRouter = APIRouter()


@LibraryRouter.get("/library")
def get_user_library(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns a list of all parent documents in the user's library.

    Parameters:
    - user_id: str
        The user's unique identifier
    - db: Session
        The database session

    Returns:
    - list[models.bookCatalogue]

    """
    return operations.get_user_library(db, user_id)


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
    document = operations.get_user_document_by_id(
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
    random_seed: Optional[int] = None,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all documents in the database.

    method: specifies order to return documents

    TODO: Check sort filter is actually valid by comparing to attributes in
    documents. What to return though? Just ignore?
    """
    if random:
        return operations.get_random_user_documents(
            db, user_id=user_id, limit=limit, random_seed=random_seed
        )

    table_columns = models.Document.__table__.columns.keys()
    if sort and sort not in table_columns:
        return HTTPException(
            status_code=400,
            detail=(
                f"Invalid sort field '{sort}' for {models.Document.__name__}."
            ),
        )

    if order_by not in ["asc", "desc"]:
        print(f"Invalid {order_by=} value. Setting to default of 'desc'.")
        order_by = "desc"

    return operations.get_user_documents(
        db,
        user_id=user_id,
        limit=limit,
        offset=offset,
        sort=sort,
        order_by=order_by,
    )


@LibraryRouter.get("/documents/{document_id}/similar")
def get_similar_documents(
    document_id: str,
    topk: int = 5,
    threshold: float = 0.5,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get semantically similar documents to a given document based on the
    content and return up to topk similar documents.
    """
    if not operations.get_user_document_by_id(db, user_id, document_id):
        return HTTPException(
            status_code=404,
            detail=(
                f"Document with {document_id=} "
                f"belonging to {user_id=} not found.",
            ),
        )

    similar_document_ids = retrieval.get_similar_user_documents(
        db, user_id, document_id, topk=topk
    )

    output = []
    for doc_id, score in similar_document_ids:
        document = operations.get_user_document_by_id(db, user_id, doc_id)
        if not document:
            logger.error(f"Document with id {doc_id} not found in database.")
            continue
        output.append(
            {
                "id": document.id,
                "title": document.title,
                "authors": document.authors,
                "document_type": document.document_type,
                "created_at": document.created_at,
                "updated_at": document.updated_at,
                "content": document.content,
                "is_clip": document.is_clip,
                "location_type": document.location_type,
                "clip_start": document.clip_start,
                "clip_end": document.clip_end,
                "catalogue_id": document.catalogue_id,
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
    return operations.search_library_by_query(db, user_id=user_id, text=query)
