from contextlib import contextmanager
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists, drop_database
from dotenv import load_dotenv
import os

from bookz.logger import app_logger

load_dotenv()

DATABASE_URL = (f"postgresql+psycopg2://{os.getenv('db_user')}:{os.getenv('db_password')}"
                f"@{os.getenv('db_url')}:{os.getenv('db_port')}/{os.getenv('db_name')}"
                f"?client_encoding=utf8")
app_logger.debug(f"DATABASE_URL={DATABASE_URL}")

# Define Base at the top level
Base = declarative_base()
engine = None
SessionLocal = None

def start_db():
    app_logger.debug(f"Calling start_db function")
    global engine, SessionLocal, Base, DATABASE_URL
    if not database_exists(DATABASE_URL):
        app_logger.debug(f"Database don't exist. Creating database {DATABASE_URL}")
        create_database(DATABASE_URL)
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    app_logger.debug(f"Created database engine {engine.url}")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

def reset_db():
    app_logger.debug(f"Calling reset_db function")
    global engine
    if not engine:
        close_db()
    engine = creat

    e_engine(DATABASE_URL, pool_pre_ping=True)
    if database_exists(engine.url):
        drop_database(engine.url)
    create_database(engine.url)
    Base.metadata.create_all(bind=engine)

def is_database_exists() -> bool:
    # Check using the database URL directly
    app_logger.debug(f"Calling is_database_exists function")
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
    app_logger.debug(f"Calling close_db function")
    global engine
    if engine:
        engine.dispose()
        engine = None