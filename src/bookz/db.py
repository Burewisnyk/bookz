from contextlib import contextmanager
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists, drop_database
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = (f"postgresql+psycopg2://{os.getenv('db_user')}:{os.getenv('db_password')}"
                f"@{os.getenv('db_url')}:{os.getenv('db_port')}/{os.getenv('db_name')}"
                f"?client_encoding=utf8")

# Define Base at the top level
Base = declarative_base()
engine = None
SessionLocal = None

def start_db():
    global engine, SessionLocal
    if engine is None:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    if not database_exists(url=engine.url):
        create_database(engine.url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

def reset_db():
    global engine
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    if database_exists(engine.url):
        drop_database(engine.url)
    create_database(engine.url)
    Base.metadata.create_all(bind=engine)

def is_database_exists() -> bool:
    # Check using the database URL directly
    return database_exists(DATABASE_URL)

@contextmanager
def get_session():
    """Provides a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def close_db():
    global engine
    if engine:
        engine.dispose()
        engine = None