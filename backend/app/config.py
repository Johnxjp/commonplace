import os
import logging

# TODO: Move all these to env files
DB_DRIVER = "postgresql"
DB_USERNAME = "postgres"
DB_NAME = "conex"
DB_HOST = "localhost"
DB_PORT = 5432

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536  # open-ai-embeddings
TFHUB_CACHE_DIR = os.path.join("dump/tfhub_models")
CHUNKING_STRATEGY = None
THRESHOLD_SCORE = 1.0
AUTHOR_SEPARATOR = ";"
MIN_CHUNK_SIZE = 20  # characters


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
