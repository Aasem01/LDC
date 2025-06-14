from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
import os
from app.models.database_models import Base
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """
    Dependency for getting DB session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize the database by creating all tables
    """
    # Ensure the SQLite directory exists
    os.makedirs(os.path.dirname(SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
    Base.metadata.create_all(bind=engine)