import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


user = 'root'
password = 'password'
db = 'flighty'

DB_URL = os.environ.get("DB_URL", default="127.0.0.1")

SQLALCHEMY_DATABASE_URL = f"mysql://{user}:{password}@{DB_URL}/{db}"

# Use pool_pre_ping to avoid "SQL server has gone away" error after 8 hours of inactivity
# more: https://docs.sqlalchemy.org/en/14/core/pooling.html#disconnect-handling-pessimistic
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    get_db

    Utility function to get the database
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()