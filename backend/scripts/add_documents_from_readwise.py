"""
First add book catalogue documents to the database by running the
add_book_catalogue.py script.

This script will add book notes from Readwise to the database.
"""

import argparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import DB_DRIVER, DB_USERNAME, DB_HOST, DB_NAME, DB_PORT
from sqlalchemy.engine import URL

from app.db import operations
from app.db.utils import convert_book_annotation_to_db_document
from app.file_handlers.readwise_parser import process_readwise_csv


# Create database URL
DB_URL = URL.create(
    drivername=DB_DRIVER,
    username=DB_USERNAME,
    host=DB_HOST,
    database=DB_NAME,
    port=DB_PORT,
)

# Create engine and session
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def main(readwise_csv: str):
    """
    Needs to look up the book in the catalogue to get the book id and
    then add the notes
    """

    print(f"Processing readwise file {readwise_csv}")
    data = process_readwise_csv(readwise_csv)

    total_items = sum([len(v) for v in data.values()])
    total_added_count = 0
    with SessionLocal() as db:
        user_id = "6d032281-9e69-4753-a455-b48f7cb9b5c9"  # temp user
        for index, ((title, authors), annotations) in enumerate(data.items()):
            print("Processing book ", index + 1, " of ", len(data))
            print(f"Adding {len(annotations)} to database")

            # TODO: Need to normalise books consistently or do smarter search.
            books = operations.search_user_books(db, user_id, title)
            if books:
                book_item = books[0]

            else:
                print(
                    f"Could not find book in catalogue with {title=} "
                    f"and {authors=}. Creating item."
                )
                book_item = operations.create_book_catalogue_item(
                    db, title, authors
                )

            for item in annotations:
                db_item = convert_book_annotation_to_db_document(
                    item, user_id, book_item
                )

                try:
                    db.add(db_item)
                    db.commit()
                    total_added_count += 1
                except Exception as e:
                    print(
                        f"Failed to add item belonging to {title} "
                        f"due to {str(e)}"
                    )
                    print(db_item)
                    db.rollback()

    print(f"Added {total_added_count} of {total_items} items to database.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "readwise_csv", type=str, help="Path to Readwise csv file"
    )
    args = parser.parse_args()
    main(args.readwise_csv)
