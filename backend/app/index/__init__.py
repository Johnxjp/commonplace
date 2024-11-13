from sentence_transformers import SentenceTransformer

from app.config import EMBEDDING_MODEL

# Doesn't work with openai embedding model
embedding_model = SentenceTransformer(EMBEDDING_MODEL)
