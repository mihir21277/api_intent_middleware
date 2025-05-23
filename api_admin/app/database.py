# api_admin/app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

Base = declarative_base()

# Create database directory if it doesn't exist
DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
os.makedirs(DATABASE_DIR, exist_ok=True)

# Database file path
DATABASE_FILE = os.path.join(DATABASE_DIR, 'api_middleware.sqlite')

# SQLAlchemy database URL
SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_FILE}"

print(f"Database will be created at: {DATABASE_FILE}")

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL query logging
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_async_session() -> AsyncSession:
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()

# Utility functions for the init script
def get_database_path() -> str:
    """Get the full path to the database file"""
    return DATABASE_FILE

def database_exists() -> bool:
    """Check if the database file exists"""
    return os.path.exists(DATABASE_FILE)