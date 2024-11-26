"""
Code for doing information retrieval.
"""

from typing import Tuple

import numpy as np
from sqlalchemy import Row
from sqlalchemy.orm import Session

from app.db import operations, models
from app.index import embedding_model

# TODO: Consider re-ranking


def retrieve_candidate_chunks(
    db: Session,
    user_id: str,
    query: str,
    topk: int = 5,
    # threshold: float = 0.5,
) -> list[Row[Tuple[models.Embedding, float]]]:
    """
    Retrieve documents from the user's library that match a query.

    # threshold is the maximum cosine distance score before not a match.
    """
    query_embedding = embedding_model.embed(query)
    return operations.get_similar_chunks(
        db, user_id, np.squeeze(query_embedding), topk=topk
    )


def get_similar_user_documents(
    db: Session, user_id: str, document_id: str, topk: int = 5
) -> list[Tuple[str, float]]:
    """
    Retrieve semantically similar documents to a query. Return a list
    of document ids and scores. Documents are ordered by best score first.

    This is quite complex as a document can have many semantically distinct
    parts. So I will take all the chunks from a document and compare those to
    the entire database of embeddings. I will take all the results and rank
    them returning the topk documents aggregated from all chunk comparisons.

    TODO: Can this be done in parallel as this is quite slow.
    """

    # Get document chunks
    document_chunks = operations.get_document_chunks(db, document_id)

    # Get similar chunks for each embedding excluding comparison with itself
    # and the document's own embeddings
    chunk_collection = {}
    for chunk in document_chunks:
        chunks = operations.get_similar_chunks(
            db,
            user_id,
            chunk.embedding,
            topk=10,
            exclude_documents=[document_id],
            exclude_chunks=None,
        )

        # Don't add duplicates
        for row in chunks:
            if (
                row.id in chunk_collection
                and row.score < chunk_collection[row.id].score
            ):
                # minumum as cosine distance is used with best value being 0
                chunk_collection[row.id] = row
            else:
                chunk_collection[row.id] = row

    # Aggregation step. A documents total score is the average of all its
    # chunks. We want to return the topk documents which is a list of tuples
    # containing the document id and the average score, ordered by highest
    # to lowest score.
    doc_scores = {}
    for chunk in chunk_collection.values():
        if chunk.source_id in doc_scores:
            doc_scores[chunk.source_id].append(chunk.score)
        else:
            doc_scores[chunk.source_id] = [chunk.score]

    # Average the scores
    for doc_id, scores in doc_scores.items():
        doc_scores[doc_id] = sum(scores) / len(scores)

    # Sort the documents by score
    sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)

    return sorted_docs[:topk]
