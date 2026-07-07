from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.conf.config import settings

engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency, яка віддає сесію БД на запит і гарантовано закриває її
    після завершення обробки, навіть якщо стався виняток.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
