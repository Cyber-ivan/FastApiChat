from sqlalchemy import create_engine, text
from config import settings
from sqlalchemy.orm import sessionmaker, DeclarativeBase

engine = create_engine(
    url=settings.database_url,
)

session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass