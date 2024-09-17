import os
import tempfile

from fastapi import APIRouter, UploadFile, HTTPException
from pydantic import BaseModel

from app.kindle_file_parser import process_kindle_file
from app import schemas
import traceback

ImportRouter = APIRouter()


class ImportResponse(BaseModel):
    new_annotation_imports: int


@ImportRouter.post("/upload")
async def import_kindle_annotations(
    file: UploadFile,
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
            status_code=404,
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

    n_inserted = 0
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = file.filename or "tmp_file"
            temp_file_path = os.path.join(temp_dir, filename)

            with open(temp_file_path, "wb") as temp_file:
                content = await file.read()
                temp_file.write(content)

            grouped_annotations = process_kindle_file(temp_file_path)
            # for (title, authors), annotations in grouped_annotations.items():
            #     books = db_operations.get_books_by_metadata(
            #         db, title, authors, return_first=True
            #     )
            #     if len(books) == 0:
            #         book = db_operations.create_book(
            #             db,
            #             schemas.BookCreate(
            #                 title=title, authors=authors, image_path=None
            #             ),
            #         )
            #         print(f"Added book to database:\n {book}")
            #     else:
            #         book = books[0]

            #     new_annotations = [
            #         schemas.AnnotationCreate(
            #             book_id=book.book_id,
            #             page_start=annotation.page_start,
            #             page_end=annotation.page_end,
            #             location_start=annotation.location_start,
            #             location_end=annotation.location_end,
            #             annotation_type=annotation.annotation_type,
            #             date_annotated=annotation.date_annotated,
            #             content=annotation.content,
            #         )
            #         for annotation in annotations
            #     ]
            #     result = db_operations.create_annotations(db, new_annotations)

            #     # Number inserted because no integrity error. This might be unique
            #     # or for some other reason
            #     n_inserted += len(result)
            #     print(
            #         f"Added {n_inserted} annotations to database for {title} by {authors}"
            #     )

    except Exception as err:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error processing file: {err}"
        ) from err

    return ImportResponse(new_annotation_imports=n_inserted)
