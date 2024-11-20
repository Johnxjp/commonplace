"""
Endpoints for importing new content into a user's knowledge base.

- Add video from youtube URL
- Add kindle annotations from file
- Add kindle annotations from scraping and reading amazon website
- Add kindle annotations from readwise (csv)
"""

import os
import logging
import tempfile

from fastapi import APIRouter, UploadFile, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db, operations as db_operations
from app.file_handlers import process_kindle_file, process_readwise_csv
from app.file_handlers.readwise_parser import validate_readwise_csv
import traceback

ImportRouter = APIRouter()
logger = logging.getLogger(__name__)


class ImportResponse(BaseModel):
    new_annotation_imports: int
    index_job_id: str = "6d032281-9e69-4753-a455-b48f7cb9b5c1"


def get_current_user() -> str:
    # TODO: Implement authentication
    return "6d032281-9e69-4753-a455-b48f7cb9b5c9"


@ImportRouter.post("/documents/upload/readwise")
async def import_book_annotations_from_readwise(
    csv_file: UploadFile,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> ImportResponse:
    """
    Import annotations from a readwise file and store those in a database.
    For an existing user, this will import any new annotations
    and add those to the database.

    It will also run a background job to chunk new annotations and generate
    embeddings.

    TODO: Handle user authentication. Otherwise can call with any id?
    """

    n_new_annos = 0
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = csv_file.filename or "tmp_file"
            temp_file_path = os.path.join(temp_dir, filename)

            with open(temp_file_path, "wb") as temp_file:
                content = await csv_file.read()
                temp_file.write(content)

            if not validate_readwise_csv(temp_file_path):
                # TODO: Any chance of more info?
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Invalid Readwise CSV file. "
                        "Please check the format.",
                    ),
                )

            # Process the file
            contents = process_readwise_csv(temp_file_path)

            # TODO: filter out notes for now
            contents = {
                key: [
                    ann for ann in value if ann.annotation_type == "Highlight"
                ]
                for key, value in contents.items()
            }

        new_inserts = []
        for (title, authors), annotations in contents.items():
            books = db_operations.find_books_in_catalogue(db, title, authors)
            if not books:
                book = db_operations.create_book_catalogue_item(
                    db, title, authors
                )
                print(f"Added book to catalogue:\n {book}")
            else:
                # Just get first for now e.g. if multiple editions
                book = books[0]

            new_inserts = db_operations.insert_book_all_documents(
                db, current_user, str(book.id), annotations
            )
            n_new_annos += len(new_inserts)

        # Run a background job to generate embeddings
        # TODO: Do we do this for all annotations at once?
        # Want to pass the job id to frontend to check status
        # Add callback?
        # index_content(new_inserts)
        return ImportResponse(
            new_annotation_imports=n_new_annos,
            index_job_id="6d032281-9e69-4753-a455-b48f7cb9b5c1",
        )

    except Exception as err:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error processing file: {err}"
        ) from err


@ImportRouter.post("/documents/upload/kindle")
async def import_kindle_annotations(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> ImportResponse:
    """
    Import annotations from a kindle file and store those in a database.
    For an existing user, this will import any new annotations
    and add those to the database.

    TODO: Handle repeated uploads by the same user.
    TODO: Run a background job for embeddings
    """
    # Error if don't receive text kindle_file
    # Note that the kindle_file has to be submitted as part of a multipart form
    # instead of a regular form data
    if file.content_type != "text/plain":
        raise HTTPException(
            status_code=400,
            detail=(
                "Unexpected file format expected 'text/plain' "
                f"but received {file.content_type}."
            ),
        )

    if file.size and file.size > 500 * 1000 * 1000:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File size {file.size} too large, "
                "expected file size to be <500Mb."
            ),
        )

    n_new_annos = 0
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = file.filename or "tmp_file"
            temp_file_path = os.path.join(temp_dir, filename)

            with open(temp_file_path, "wb") as temp_file:
                content = await file.read()
                temp_file.write(content)

            grouped_annotations = process_kindle_file(temp_file_path)
            logger.info(
                f"Found annotation from {len(grouped_annotations)} "
                "unique books"
            )
            for (title, authors), annotations in grouped_annotations.items():
                books = db_operations.find_books_in_catalogue(
                    db,
                    title,
                    authors,
                )
                if len(books) == 0:
                    book = db_operations.create_book_catalogue_item(
                        db, title, authors, thumbnail_path=None
                    )
                    print(f"Added book to catalogue:\n {book}")
                else:
                    # Just get first for now e.g. if multiple editions
                    book = books[0]

                new_inserts = db_operations.insert_book_all_documents(
                    db, current_user, str(book.id), annotations
                )
                n_new_annos += len(new_inserts)

            return ImportResponse(
                new_annotation_imports=n_new_annos,
                index_job_id="6d032281-9e69-4753-a455-b48f7cb9b5c1",
            )

    except Exception as err:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error processing file: {err}"
        ) from err
