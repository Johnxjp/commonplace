import os
import logging

# TODO: Move all these to env files
DB_DRIVER = "postgresql"
DB_USERNAME = "postgres"
DB_NAME = "conex"
DB_HOST = "localhost"
DB_PORT = 5432

EMBEDDING_DIMENSIONS = 512
TFHUB_CACHE_DIR = os.path.join("dump/tfhub_models")
CHUNKING_STRATEGY = None
THRESHOLD_SCORE = 1.0
AUTHOR_SEPARATOR = ";"


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
