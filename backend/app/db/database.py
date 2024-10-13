from typing import Any, Generator
import logging

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, Session

from app.config import DB_DRIVER, DB_USERNAME, DB_HOST, DB_NAME, DB_PORT
from app.db.models import Base

logger = logging.getLogger(__name__)

DB_URL = URL.create(
    drivername=DB_DRIVER,
    username=DB_USERNAME,
    host=DB_HOST,
    database=DB_NAME,
    port=DB_PORT,
)

engine = create_engine(DB_URL)
# Session maker is a factory for making session objects
SessionLocal = sessionmaker(autocommit=False, bind=engine)

# Create all tables in the database
with psycopg2.connect(
    dbname=DB_NAME, user=DB_USERNAME, host=DB_HOST, port=DB_PORT
) as conn:
    logger.info("Initialising database")
    with conn.cursor() as cursor:
        # TODO: Move these into an SQL File and Run it.
        cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

Base.metadata.create_all(bind=engine, checkfirst=True)


# Dependency
def get_db() -> Generator[Session, Any, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
