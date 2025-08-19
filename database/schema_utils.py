"""
Database schema utilities for handling schema migrations
"""

from typing import List, Set
from sqlalchemy import text
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class SchemaChecker:
    def __init__(self):
        self._cached_columns = {}
    
    def get_table_columns(self, session: Session, table_name: str) -> Set[str]:
        """Get all columns for a table, with caching"""
        if table_name in self._cached_columns:
            return self._cached_columns[table_name]
        
        try:
            # Try MySQL/MariaDB first
            result = session.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = :table_name 
                AND TABLE_SCHEMA = DATABASE()
            """), {"table_name": table_name})
            
            columns = {row[0] for row in result.fetchall()}
            
            if not columns:
                # Try PostgreSQL
                result = session.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = :table_name
                """), {"table_name": table_name})
                columns = {row[0] for row in result.fetchall()}
            
            self._cached_columns[table_name] = columns
            return columns
            
        except Exception as e:
            logger.warning(f"Could not check table columns for {table_name}: {e}")
            # Return empty set as fallback
            return set()
    
    def has_columns(self, session: Session, table_name: str, column_names: List[str]) -> bool:
        """Check if table has all specified columns"""
        existing_columns = self.get_table_columns(session, table_name)
        return all(col in existing_columns for col in column_names)
    
    def has_column(self, session: Session, table_name: str, column_name: str) -> bool:
        """Check if table has a specific column"""
        existing_columns = self.get_table_columns(session, table_name)
        return column_name in existing_columns
    
    def clear_cache(self):
        """Clear the column cache"""
        self._cached_columns.clear()

# Global schema checker instance
schema_checker = SchemaChecker()

def check_content_schema_migration(session: Session) -> bool:
    """Check if content management schema migration has been applied"""
    required_columns = ['link_url', 'movie_name', 'local_status', 'edited_status', 'content_to_add', 'source_folder']
    return schema_checker.has_columns(session, 'content_items', required_columns)

def get_safe_content_query_fields(session: Session) -> List[str]:
    """Get list of safe fields to query from content_items table"""
    base_fields = [
        'id', 'name', 'content_type', 'status', 'priority', 
        'description', 'file_path', 'file_size_bytes', 'duration_seconds',
        'thumbnail_url', 'video_url', 'metadata', 'movie_id',
        'created_at', 'updated_at', 'uploaded_at', 'processed_at'
    ]
    
    # Additional fields that might be new
    optional_fields = ['link_url', 'movie_name', 'local_status', 'edited_status', 'content_to_add', 'source_folder']
    
    # Check which optional fields exist
    safe_fields = base_fields.copy()
    for field in optional_fields:
        if schema_checker.has_column(session, 'content_items', field):
            safe_fields.append(field)
    
    return safe_fields