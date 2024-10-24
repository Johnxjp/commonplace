# from uuid import uuid4

# from redis import Redis
# from rq import Queue

from sqlalchemy.orm import Session

from app.db import models
from app.db.operations import insert_embeddings
from app.index.preprocessing import multisentence_tokeniser
from app.index.vectoriser import embed

# redis_conn = Redis()
# q = Queue("index", connection=redis_conn)


# def create_index_annotation(
#     annotation: models.BookDocument | models.VideoDocument,
# ) -> None:
#     """
#     This will embed the text and add it to the search index.
#     """
#     for embed in enumerate(annotation.embeddings):

#     q.enqueue(embed, annotation)


# def create_annotation_index_job(
#     annotation: list[models.BookDocument | models.VideoDocument],
# ) -> str:
#     job_id = str(uuid4())
#     q.enqueue(embed, job_id=job_id)
#     return job_id


def index_content(
    db: Session,
    documents: list[models.BookDocument | models.VideoDocument],
) -> list[models.Embeddings]:
    """
    Index content into the search index.
    """
    embedding_rows = []
    for doc in documents:
        content = doc.content
        n_overlap = 0
        ngroup = 3
        chunking_strategy = "sent-group-{ngroup}-overlap-{n_overlap}"
        chunked_content = multisentence_tokeniser(content, n_overlap, ngroup)
        for chunk in chunked_content:
            embedding = embed(chunk)
            embedding_rows.append(
                models.Embeddings(
                    source_id=doc.id,
                    chunk_content=content,
                    cleaned_chunk=content,
                    chunking_strategy=chunking_strategy,
                    embedding=embedding,
                )
            )

    return insert_embeddings(db, embedding_rows)
