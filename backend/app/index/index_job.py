# from uuid import uuid4

# from redis import Redis
# from rq import Queue

from sqlalchemy.orm import Session

from app.config import MIN_CHUNK_SIZE
from app.db import models
from app.db.operations import insert_embeddings
from app.index.preprocessing import multisentence_tokeniser
from app.index import embedding_model


def index_content(
    db: Session,
    documents: list[models.Document],
) -> None:
    """
    Index content into the search index.
    """
    embedding_rows = []
    for doc in documents:
        content = doc.content
        group_overlap = 1
        max_sentences = 3
        chunking_strategy = (
            "sent-group-{max_sentences}-overlap-{group_overlap}"
        )
        # There may be token limit considerations for embedding models.
        chunked_content = multisentence_tokeniser(
            content,
            max_sentences,
            group_overlap,
            min_characters=MIN_CHUNK_SIZE,
        )
        for chunk in chunked_content:
            embedding = embedding_model.embed(chunk)
            embedding_rows.append(
                models.Embedding(
                    source_id=doc.id,
                    chunk_content=content,
                    cleaned_chunk=content,
                    chunking_strategy=chunking_strategy,
                    embedding=embedding,
                )
            )

    insert_embeddings(db, embedding_rows)
