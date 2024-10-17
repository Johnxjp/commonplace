import argparse
from typing import Optional

from sqlalchemy import create_engine, text
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


def init_db(table: Optional[str] = None, add_dummy_user: bool = False):
    print("Initializing database...")

    # Create a session
    db = SessionLocal()

    try:
        # Create extensions
        db.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        db.commit()
        print("Extensions created successfully.")

        # Create all tables
        if table and table in Base.metadata.tables:
            table_obj = Base.metadata.tables[table]
            Base.metadata.create_all(bind=engine, tables=[table_obj])
            print(f"{table} created successfully.")
        else:
            Base.metadata.create_all(bind=engine)
            print("All tables created successfully.")

        if add_dummy_user:
            # Add a dummy user with id "6d032281-9e69-4753-a455-b48f7cb9b5c9"
            # with created_at now
            db.execute(
                text(
                    """
                    INSERT INTO "user" (id, created_at)
                    VALUES ('6d032281-9e69-4753-a455-b48f7cb9b5c9', now());
                    """
                )
            )
            db.commit()
            print("Dummy user added successfully.")

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
    parser.add_argument(
        "--add_dummy_user", action="store_true", help="Add a dummy user."
    )
    args = parser.parse_args()

    init_db(args.table, args.add_dummy_user)
