import argparse
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import DB_DRIVER, DB_USERNAME, DB_HOST, DB_NAME, DB_PORT
from app.db.models import Base
from sqlalchemy.engine import URL


# Create database URL
DB_URL = URL.create(
    drivername=DB_DRIVER,
    username=DB_USERNAME,
    host=DB_HOST,
    database=DB_NAME,
    port=DB_PORT,
)

# Create engine and session
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def delete_db(table: Optional[str] = None):
    print("Deleting database...")

    # Create a session
    db = SessionLocal()

    try:
        if table and table in Base.metadata.tables:
            table_obj = Base.metadata.tables[table]
            Base.metadata.drop_all(bind=engine, tables=[table_obj])
            print(f"{table} deleted successfully.")
        else:
            Base.metadata.drop_all(bind=engine)
            print("All tables deleted successfully.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Utilities to interact with database."
    )
    parser.add_argument("--table", type=str, help="Table to interact with.")
    args = parser.parse_args()

    delete_db(args.table)
