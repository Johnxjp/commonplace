import os

# TODO: Move all these to env files
DB_DRIVER = "postgresql"
DB_USERNAME = "postgres"
DB_NAME = "conex"
DB_HOST = "localhost"
DB_PORT = 5432

QUERY_DECOMPOSITION_MODEL = "gpt-4o-mini"
ANSWER_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536  # open-ai-embeddings
TFHUB_CACHE_DIR = os.path.join("dump/tfhub_models")
CHUNKING_STRATEGY = None
THRESHOLD_SCORE = 0.6
AUTHOR_SEPARATOR = ";"
MIN_CHUNK_SIZE = 20  # characters
