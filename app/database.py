from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database credentials from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

# Construct PostgreSQL URL
# Format: postgresql://user:password@host:port/dbname
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# For local development fallback to SQLite if env vars not set
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
    print("WARNING: Database environment variables not set. Using SQLite fallback.")
    DATABASE_URL = "sqlite:///./swipe_interview.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    print(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT}/{DB_NAME}")
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using them
        pool_size=10,  # Number of connections to maintain
        max_overflow=20,  # Max connections beyond pool_size
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
