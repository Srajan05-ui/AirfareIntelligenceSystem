import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime

logger = logging.getLogger(__name__)

# Base class for SQLAlchemy ORM models
Base = declarative_base()

class DBFareObservation(Base):
    __tablename__ = "fare_observations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_tier = Column(String(50), nullable=False)
    origin = Column(String(3), nullable=False)
    destination = Column(String(3), nullable=False)
    departure_date = Column(String(10), nullable=False)
    airline = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(String(30), nullable=False)
    
    # Cleaning Flags
    is_duplicate = Column(Boolean, default=False)
    is_outlier = Column(Boolean, default=False)
    outlier_method = Column(String(50), nullable=True) # e.g., 'MAD_Z_SCORE'

def get_engine():
    """
    Returns an SQLAlchemy engine with connection pooling enabled.
    Ensures pre_ping is True to prevent silent disconnects with cloud databases (like Supabase).
    """
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        # Fallback to local SQLite for prototype dev
        logger.warning("No DATABASE_URL found. Using local SQLite.")
        db_url = "sqlite:///local_airfare.db"
    
    engine = create_engine(
        db_url,
        pool_pre_ping=True,  # Critical for Supabase/Cloud stability
        pool_size=5,
        max_overflow=10
    )
    return engine

def init_db():
    """Create all tables if they don't exist"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()
