"""
Database initialization script for Supabase PostgreSQL
Run this script to create tables in your Supabase database
"""
from app.database import engine, Base
from app.models import Candidate, Interview
from sqlalchemy import text

def init_db():
    """Create all tables in the database"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    
    # Verify connection
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()
        print(f"Connected to PostgreSQL: {version[0]}")

if __name__ == "__main__":
    init_db()
