#SQLAlchemy, database connection and session management

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL


# This initializes the connection pool to PostgreSQL
engine = create_engine(DATABASE_URL)



# Each request will create a new "SessionLocal" instance
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# All database models (User, Loan) must inherit from this class
Base = declarative_base()


# This function creates a fresh session for a request and closes it immediately after
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()