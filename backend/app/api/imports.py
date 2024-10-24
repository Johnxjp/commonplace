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

from app.db import get_db, operations as db_operations, models
from app.file_handlers import process_kindle_file, process_readwise_csv
from app.file_handlers.readwise_parser import validate_readwise_csv
from app.index import preprocessing
from app.index.embedding_job import index_content
import traceback

ImportRouter = APIRouter()
logger = logging.getLogger(__name__)


class ImportResponse(BaseModel):
    new_annotation_imports: int
    job_id: str = "6d032281-9e69-4753-a455-b48f7cb9b5c1"


def index_book_annotations(annotations: list[models.BookDocument]) -> None:
    """
    Index annotations for a book in the search index.

    This will allow users to search for annotations by content.
    """
    for annotation in annotations:
        # Index the annotation
        annotation


def get_current_user() -> str:
    # TODO: Implement authentication
    return "6d032281-9e69-4753-a455-b48f7cb9b5c9"


@ImportRouter.post("/documents/youtube")
async def import_youtube_video(url: str):
    """
    Import a youtube video into the database from a url.

    Obtain the transcript and run a background job to generate embeddings.

    A url could contain query parameters. We need to determine if there
    is a start and end time for a clip. If so, we need to store that as well.

    Finally strip query parameters and store the base url of the video with
    the id of the video.

    Video URL: https://www.youtube.com/watch?v=e049IoFBnLA
    Video URL (alternate): https://youtu.be/e049IoFBnLA?si=Is47s6ro2VkX1Y7I
    Video URL with clip: https://youtu.be/e049IoFBnLA?si=F4TVYyspemPRGyod&t=918
    Video URL with start / end: https://youtube.com/embed/7RnLBsSi9UI?start=165&end=228
    """
    pass


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

    TODO: Handle authentication. Otherwise can call with any id?
    """

    # TODO: Some kind of validation for the file
    # If I was a user and uploaded a document that was badly formatted
    # or misinterpreted, I would want to know that the file was not processed
    # correctly and there was a way to undo. Otherwise if it polluted
    # my database, I would be very upset especially with a large volume
    # of annotations.

    n_new_annos = 0
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = csv_file.filename or "tmp_file"
            temp_file_path = os.path.join(temp_dir, filename)

            with open(temp_file_path, "wb") as temp_file:
                content = await csv_file.read()
                temp_file.write(content)

            if not validate_readwise_csv(temp_file_path):
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

            # Find or add book to catalogue
            # Does the catalogue need to be by user?
            books = db_operations.search_book_by_metadata(db, title, authors)
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
            n_new_annos = len(new_inserts)

        # Run a background job to generate embeddings
        # TODO: Do we do this for all annotations at once?
        # Want to pass the job id to frontend to check status
        # Add callback?
        index_content(new_inserts)
        return ImportResponse(
            new_annotation_imports=n_new_annos,
            job_id="6d032281-9e69-4753-a455-b48f7cb9b5c1",
        )

    except Exception as err:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error processing file: {err}"
        ) from err

        # Check existing annotations


# @ImportRouter.post("/upload")
# async def import_kindle_annotations(
#     file: UploadFile,
# ) -> ImportResponse:
#     """
#     Import annotations from a kindle file and store those in a database.
#     For an existing user, this will import any new annotations
#     and add those to the database.

#     TODO: Handle repeated uploads by the same user.
#     TODO: Run a background job for embeddings
#     """
#     # Error if don't receive text kindle_file
#     # Note that the kindle_file has to be submitted as part of a multipart form
#     # instead of a regular form data
#     if file.content_type != "text/plain":
#         raise HTTPException(
#             status_code=404,
#             detail=(
#                 "Unexpected file format expected 'text/plain' "
#                 f"but received {file.content_type}."
#             ),
#         )

#     if file.size and file.size > 500 * 1000 * 1000:
#         raise HTTPException(
#             status_code=413,
#             detail=(
#                 f"File size {file.size} too large, "
#                 "expected file size to be <500Mb."
#             ),
#         )

#     n_inserted = 0
#     try:
#         with tempfile.TemporaryDirectory() as temp_dir:
#             filename = file.filename or "tmp_file"
#             temp_file_path = os.path.join(temp_dir, filename)

#             with open(temp_file_path, "wb") as temp_file:
#                 content = await file.read()
#                 temp_file.write(content)

#             grouped_annotations = process_kindle_file(temp_file_path)
#             logger.info(
#                 f"Found annotation from {len(grouped_annotations)} unique books"
#             )
#             for (title, authors), annotations in grouped_annotations.items():
#                 books = db_operations.get_books_by_metadata(
#                     db, title, authors, return_first=True
#                 )
#                 if len(books) == 0:
#                     book = db_operations.create_book(
#                         db,
#                         schemas.BookCreate(
#                             title=title, authors=authors, image_path=None
#                         ),
#                     )
#                     print(f"Added book to database:\n {book}")
#                 else:
#                     book = books[0]

#                 new_annotations = [
#                     schemas.AnnotationCreate(
#                         book_id=book.book_id,
#                         page_start=annotation.page_start,
#                         page_end=annotation.page_end,
#                         location_start=annotation.location_start,
#                         location_end=annotation.location_end,
#                         annotation_type=annotation.annotation_type,
#                         date_annotated=annotation.date_annotated,
#                         content=annotation.content,
#                     )
#                     for annotation in annotations
#                 ]
#                 result = db_operations.create_annotations(db, new_annotations)

#                 # Number inserted because no integrity error. This might be unique
#                 # or for some other reason
#                 n_inserted += len(result)
#                 print(
#                     f"Added {n_inserted} annotations to database for {title} by {authors}"
#                 )

#     except Exception as err:
#         traceback.print_exc()
#         raise HTTPException(
#             status_code=500, detail=f"Error processing file: {err}"
#         ) from err

#     return ImportResponse(new_annotation_imports=n_inserted)
