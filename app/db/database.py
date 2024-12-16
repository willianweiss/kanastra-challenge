import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.utils.config import settings

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:5432/{settings.POSTGRES_DB}",
)
TABLE_NAME = "debt"

engine = create_engine(DATABASE_URL, echo=True, future=True)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
