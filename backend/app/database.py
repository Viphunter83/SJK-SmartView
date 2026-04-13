import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Если URL отсутствует, используем SQLite для локальной разработки (fallback)
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    DATABASE_URL, 
    # check_same_thread нужно только для SQLite
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
