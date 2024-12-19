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
import traceback

from app.api.auth import get_current_user
from app.db import get_db, operations
from app.file_handlers import process_kindle_file, process_readwise_csv
from app.file_handlers.readwise_parser import validate_readwise_csv
from app.schemas import BookAnnotationType
from app.utils import hash_content

ImportRouter = APIRouter()
logger = logging.getLogger(__name__)


class ImportResponse(BaseModel):
    total_documents: int
    total_clips: int
    new_clip_inserts: int
    embedding_index_job_id: str = "6d032281-9e69-4753-a455-b48f7cb9b5c1"


@ImportRouter.post("/document/upload/readwise")
async def import_book_annotations_from_readwise(
    csv_file: UploadFile,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> ImportResponse:
    """
    Import annotations from a readwise file and store those in a database.
    For an existing user, this will import any new annotations
    and add those to the database.

    It will also run a background job to chunk new annotations and generate
    embeddings.
    """
    logger.info(f"Importing annotations from Readwise for user {user_id}")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = csv_file.filename or "tmp_file"
            temp_file_path = os.path.join(temp_dir, filename)

            with open(temp_file_path, "wb") as temp_file:
                content = await csv_file.read()
                temp_file.write(content)

            if not validate_readwise_csv(temp_file_path):
                # TODO: Any chance of more info? Have to break this function down
                # To detect what is missing and return status message
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
                ann
                for ann in value
                if ann.annotation_type == BookAnnotationType.HIGHLIGHT.value
            ]
            for key, value in contents.items()
        }

        document_values = []
        for title, authors in contents.keys():
            books = operations.find_catalogue_books(db, title, authors)
            catalogue_id = str(books[0].id) if len(books) else None
            document_values.append(
                {
                    "user_id": user_id,
                    "title": title,
                    "authors": authors,
                    "user_thumbnail_path": None,
                    "catalogue_id": catalogue_id,
                }
            )

        # This returns all documents that were inserted or existing
        documents = operations.insert_documents(db, document_values)
        # Create all clips at once

        total_clips = 0
        new_inserts = 0
        for doc in documents:
            all_clips = []
            annotations = contents[(doc.title, doc.authors)]
            doc_clips = [
                {
                    "user_id": user_id,
                    "document_id": doc.id,
                    # "clipped_at": annotation.date_annotated,
                    # "original_content": annotation.content,
                    "content": annotation.content,
                    "content_hash": hash_content(annotation.content),
                    "location_type": annotation.location_type,
                    "clip_start": annotation.location_start,
                    "clip_end": annotation.location_end,
                }
                for annotation in annotations
            ]
            all_clips.extend(doc_clips)
            successful_inserts = operations.insert_clips(db, all_clips)
            new_inserts += len(successful_inserts)

        # Run a background job to generate embeddings
        # TODO: Do we do this for all annotations at once?
        # Want to pass the job id to frontend to check status
        # Add callback?
        return ImportResponse(
            total_documents=len(contents),
            total_clips=total_clips,
            new_clip_inserts=new_inserts,
        )

    except Exception as err:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error processing file: {err}"
        ) from err


@ImportRouter.post("/document/upload/kindle")
async def import_kindle_annotations(
    file: UploadFile,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
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

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = file.filename or "tmp_file"
            temp_file_path = os.path.join(temp_dir, filename)

            with open(temp_file_path, "wb") as temp_file:
                content = await file.read()
                temp_file.write(content)

            contents = process_kindle_file(temp_file_path)
            logger.info(
                f"Found annotation from {len(contents)} " "unique books"
            )

        # TODO: filter out notes for now
        contents = {
            key: [
                ann
                for ann in value
                if ann.annotation_type == BookAnnotationType.HIGHLIGHT.value
            ]
            for key, value in contents.items()
        }

        document_values = []
        for title, authors in contents.keys():
            books = operations.find_catalogue_books(db, title, authors)
            catalogue_id = str(books[0].id) if len(books) else None
            document_values.append(
                {
                    "user_id": user_id,
                    "title": title,
                    "authors": authors,
                    "user_thumbnail_path": None,
                    "catalogue_id": catalogue_id,
                }
            )

        # This returns all documents that were inserted or existing
        documents = operations.insert_documents(db, document_values)
        # Create all clips at once
        all_clips = []
        for doc in documents:
            annotations = contents[(doc.title, doc.authors)]
            doc_clips = [
                {
                    "user_id": user_id,
                    "document_id": doc.id,
                    # "clipped_at": annotation.date_annotated,
                    # "original_content": annotation.content,
                    "content": annotation.content,
                    "content_hash": hash_content(annotation.content),
                    "location_type": annotation.location_type,
                    "clip_start": annotation.location_start,
                    "clip_end": annotation.location_end,
                }
                for annotation in annotations
            ]
            all_clips.extend(doc_clips)

        logger.info(all_clips[0])
        successful_inserts = operations.insert_clips(db, all_clips)
        n_new_annos = len(successful_inserts)

        # Run a background job to generate embeddings
        # TODO: Do we do this for all annotations at once?
        # Want to pass the job id to frontend to check status
        # Add callback?
        return ImportResponse(
            total_documents=len(contents),
            total_clips=len(all_clips),
            new_clip_inserts=n_new_annos,
        )

    except Exception as err:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error processing file: {err}"
        ) from err
