"""
Database connection and session management for CineMitr
"""

import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
import logging
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

Base = declarative_base()

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialized = False

    def initialize(self, database_url: Optional[str] = None):
        """Initialize database connection"""
        if self._initialized:
            return

        if not database_url:
            database_url = self._build_database_url()

        try:
            self.engine = create_engine(
                database_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=os.getenv("DATABASE_DEBUG", "false").lower() == "true"
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            self._initialized = True
            logger.info("Database connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {str(e)}")
            raise

    def _build_database_url(self) -> str:
        """Build database URL from environment variables"""
        db_driver = os.getenv("DATABASE_DRIVER", "mysql+pymysql")
        db_user = os.getenv("DATABASE_USER", "root")
        db_password = os.getenv("DATABASE_PASSWORD", "")
        db_host = os.getenv("DATABASE_HOST", "localhost")
        db_port = os.getenv("DATABASE_PORT", "3306")
        db_name = os.getenv("DATABASE_NAME", "cinemitr_db")
        
        # URL encode password to handle special characters
        db_password_encoded = quote_plus(db_password) if db_password else ""
        
        if db_password_encoded:
            database_url = f"{db_driver}://{db_user}:{db_password_encoded}@{db_host}:{db_port}/{db_name}"
        else:
            database_url = f"{db_driver}://{db_user}@{db_host}:{db_port}/{db_name}"
        
        return database_url

    @contextmanager
    def get_session(self):
        """Get database session with context manager"""
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()

    def get_session_factory(self):
        """Get session factory for dependency injection"""
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.SessionLocal

    def create_tables(self):
        """Create all database tables"""
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {str(e)}")
            raise

    def drop_tables(self):
        """Drop all database tables (use with caution)"""
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {str(e)}")
            raise

    def test_connection(self) -> bool:
        """Test database connection"""
        if not self._initialized:
            return False
        
        try:
            from sqlalchemy import text
            with self.get_session() as session:
                result = session.execute(text("SELECT 1"))
                return result.fetchone() is not None
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False

# Global database manager instance
db_manager = DatabaseManager()

# Dependency for FastAPI
def get_db() -> Session:
    """FastAPI dependency for getting database session"""
    with db_manager.get_session() as session:
        yield session