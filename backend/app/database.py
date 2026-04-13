import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

# If URL is missing, use SQLite for local development (fallback)
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./sql_app.db"
    logger.info("Database: using local SQLite (sql_app.db)")
else:
    # Railway/Production specific: Ensure SSL mode for PostgreSQL
    if DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://"):
        logger.info("Database: using production PostgreSQL")
        if "sslmode" not in DATABASE_URL:
            separator = "?" if "?" not in DATABASE_URL else "&"
            DATABASE_URL += f"{separator}sslmode=require"
    else:
        logger.info(f"Database: using external URL ({DATABASE_URL.split('://')[0]})")

engine = create_engine(
    DATABASE_URL, 
    # check_same_thread only required for SQLite
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
