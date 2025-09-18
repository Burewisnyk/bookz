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
db_name = os.getenv('db_name')


if not database_exists(DATABASE_URL):
    create_database(DATABASE_URL)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)

def reset_db():
    global engine, SessionLocal
    engine.dispose()
    if database_exists(engine.url):
        drop_database(engine.url)
    create_database(DATABASE_URL)
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

def database_exists() -> bool:
    return database_exists(DATABASE_URL)

@contextmanager
def get_context_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def close_db():
    global engine
    engine.dispose()
