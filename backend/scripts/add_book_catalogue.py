import argparse
import json

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import DB_DRIVER, DB_USERNAME, DB_HOST, DB_NAME, DB_PORT
from sqlalchemy.engine import URL


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


def add_items(data):
    """
    Data is in the format
    [
        {
            "title": "Book Title",
            "authors": "Author 1;Author 2",
            "thumbnail_path": "path/to/image"
        },
        {
            "title": "Book Title",
            "authors": "",
            "thumbnail_path": null
        }
    ]
    """
    print("Initializing database...")

    # Create a session
    db = SessionLocal()

    for item in data:
        try:
            # Add data to book_catalogue table
            if item["authors"] == "":
                item["authors"] = None

            db.execute(
                text(
                    "INSERT INTO book_catalogue (title, authors, thumbnail_path) "
                    "VALUES (:title, :authors, :thumbnail_path)"
                ),
                item,
            )
            db.commit()
            print(f"Added {item['title']} to database.")

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            db.rollback()

    db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, help="Path to json items")
    args = parser.parse_args()

    with open(args.path, "r") as f:
        data = json.load(f)

    add_items(data)
