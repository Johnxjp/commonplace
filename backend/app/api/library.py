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
# from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db, operations

logger = logging.getLogger(__name__)


LibraryRouter = APIRouter()


@LibraryRouter.get("/library")
def get_library(user_id: str, db: Session = Depends(get_db)):
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
    return operations.get_library(db, user_id)


@LibraryRouter.get("/documents/{document_id}")
def get_document(
    document_id: str, user_id: str, db: Session = Depends(get_db)
):
    """
    Get a document by its id. A document can be a book or a video and therefore
    need to check both sources.
    """

    # No unified source table so need to check all document source tables
    document = operations.get_user_document_by_id(
        db,
        document_id,
        user_id,
    )
    if not document:
        return HTTPException(
            status_code=404,
            detail=f"Document with {id=} belonging to {user_id=} not found.",
        )
    return document


# @LibraryRouter.get("/documents")
# def get_documents(
#     user_id: str,
#     limit: Optional[int] = 10,
#     offset: Optional[int] = 0,
#     sort: Optional[str] = "created_at",
#     order_by: Optional[str] = "desc",
#     random: bool = False,
#     random_seed: Optional[int] = None,
#     db: Session = Depends(get_db),
# ):
#     """
#     Get all documents in the database.

#     method: specifies order to return documents

#     TODO: Check sort filter is actually valid by comparing to attributes in
#     documents. What to return though? Just ignore?
#     """
#     if random:
#         return operations.get_random_documents(
#             db, user_id=user_id, limit=limit, offset=offset, seed=random_seed
#         )

#     return operations.get_documents_by_user(
#         db,
#         user_id=user_id,
#         limit=limit,
#         offset=offset,
#         sort=sort,
#         order_by=order_by,
#         random=random,
#         seed=random_seed,
#     )


# @LibraryRouter.get("/documents/{document_id}/similar")
# def get_similar_documents(
#     document_id: str, nmax: int = 5, db: Session = Depends(get_db)
# ):
#     """
#     Get similar documents to a given document. This will perform a semantic
#     similarity search based on the content and return up to nmax similar items
#     """
#     pass


# @LibraryRouter.post("/documents/search")
# def get_similar_documents(
#     text: str,
#     nmax: int = 5,
#     is_keyword: bool = False,  # TODO: When keyword? Always exact match?
#     db: Session = Depends(get_db),
# ):
#     """
#     Get similar documents to a given document. This will perform a semantic
#     similarity search based on the content and return up to nmax similar items
#     """
#     pass


@LibraryRouter.post("/library/search")
def library_search(
    query: str,
    user_id: str,
    db: Session = Depends(get_db),
):
    """
    Searches the library for any exact matches on either the title or author.
    Returns items based on match.
    """
    return operations.search_library_by_query(db, user_id=user_id, text=query)
