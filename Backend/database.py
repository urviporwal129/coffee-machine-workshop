# database.py
# ------------------------------------------------------
# This file sets up the connection to our SQLite database.
# Every other file (models.py, main.py) will import from here.
# ------------------------------------------------------

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# This tells SQLAlchemy to use a file called "coffee.db"
# sitting in the same folder as this script.
# SQLite will create this file automatically the first time we run the app.
DATABASE_URL = "sqlite:///./coffee.db"

# The "engine" is the actual connection to the database file.
# connect_args is only needed for SQLite (not for other databases like Postgres).
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal is a "factory" that creates a new database session
# every time we need to talk to the database (e.g. during a request).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class that all our table models (in models.py) will inherit from.
# SQLAlchemy uses this to know which Python classes represent database tables.
Base = declarative_base()


# get_db() is used by FastAPI to open a session for each request
# and automatically close it afterwards, even if an error happens.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()