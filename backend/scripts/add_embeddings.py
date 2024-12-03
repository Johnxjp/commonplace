"""
Add openai embeddings to database.
"""

import argparse

import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import DB_DRIVER, DB_USERNAME, DB_HOST, DB_NAME, DB_PORT
from sqlalchemy.engine import URL
from tqdm import tqdm

from app.utils import hash_content
from app.db import operations, models


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


def main(
    user_id: str, document_source_file: str, embeddings_file: str | None = None
):
    """
    Add embeddings to the database for all documents.
    """
    with open(document_source_file, "r") as f:
        data = pd.read_csv(f)

    embeddings = []
    if embeddings_file:
        embeddings = np.load(embeddings_file)
    else:
        print("Creating embeddings from documents.")

    assert len(data) == len(
        embeddings
    ), "Number of embeddings must match number of chunks in source file."

    text_chunks = data["chunk"].values
    source_text = data["highlight"].values
    with SessionLocal() as db:
        for chunk, source, embedding in tqdm(
            zip(text_chunks, source_text, embeddings),
            total=len(text_chunks),
        ):
            clips = operations.find_matching_clips(
                db, user_id, hash_content(source)
            )
            if not clips:
                print("Could not find source for chunk '{chunk}'.")

            for document in clips:
                source_id = document.id
                embedding_model = models.Embedding(
                    source_id=source_id,
                    chunk_content=chunk,
                    cleaned_chunk=chunk,
                    embedding=embedding,
                )
                try:
                    db.add(embedding_model)
                    db.commit()
                except Exception as e:
                    print(
                        f"Could not insert embedding for {chunk}\n"
                        f"Source: {source}\n"
                    )
                    print(f"Error: {e}")
                    db.rollback()


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "--document-source-file",
        type=str,
        required=True,
        help="File containing the source text for the document.",
    )
    args.add_argument(
        "--embeddings-file",
        type=str,
        required=False,
        help="File containing the embeddings for the documents.",
    )
    args.add_argument(
        "--user-id",
        type=str,
        default="6d032281-9e69-4753-a455-b48f7cb9b5c9",
        help="User ID to associate with the documents.",
    )
    args = args.parse_args()

    main(args.user_id, args.document_source_file, args.embeddings_file)
