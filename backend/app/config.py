from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

# TODO: Move all these to env files
DB_DRIVER = os.getenv("DB_DRIVER", "postgresql")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 5432))
QUERY_DECOMPOSITION_MODEL = os.getenv("QUERY_DECOMPOSITION_MODEL")
ANSWER_MODEL = os.getenv("ANSWER_MODEL")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", 1536))
CHUNKING_STRATEGY = (
    os.getenv("CHUNKING_STRATEGY", "")
    if os.getenv("CHUNKING_STRATEGY")
    else None
)
THRESHOLD_SCORE = float(os.getenv("THRESHOLD_SCORE", 0.6))
AUTHOR_SEPARATOR = os.getenv("AUTHOR_SEPARATOR", ";")
MIN_CHUNK_SIZE = int(os.getenv("MIN_CHUNK_SIZE", 20))
