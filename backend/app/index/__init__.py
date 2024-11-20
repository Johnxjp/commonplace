import os

from app.config import EMBEDDING_MODEL
from app.index.openai import OpenAIEmbedder

api_key = os.getenv("OPENAI_API_KEY", "")

# Doesn't work with openai embedding model
embedding_model = OpenAIEmbedder(api_key=api_key, model_name=EMBEDDING_MODEL)
