#!/usr/bin/env python3
"""
Simple database initialization script for CineMitr
Creates basic tables without triggers
"""

import os
from sqlalchemy import text
from database.connection import db_manager
from utils.logger import setup_logger

logger = setup_logger(__name__)

def init_database_simple():
    """Initialize the database with basic schema"""
    try:
        logger.info("Starting simple database initialization...")
        
        # Initialize database connection
        db_manager.initialize()
        
        # Test connection
        if not db_manager.test_connection():
            logger.error("Database connection test failed")
            return False
        
        logger.info("Database connection successful")
        
        # Simple table creation - just the essentials
        sql_statements = [
            # Users table
            """
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
                username VARCHAR(50) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                role ENUM('admin', 'editor', 'viewer') NOT NULL DEFAULT 'viewer',
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                last_login TIMESTAMP NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """,
            
            # Movies table
            """
            CREATE TABLE IF NOT EXISTS movies (
                id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
                title VARCHAR(255) NOT NULL,
                genre VARCHAR(100) NOT NULL,
                release_date DATE NULL,
                duration_minutes INT NULL,
                description TEXT NULL,
                director VARCHAR(255) NULL,
                rating VARCHAR(10) NULL,
                language VARCHAR(50) NULL,
                country VARCHAR(100) NULL,
                poster_url TEXT NULL,
                trailer_url TEXT NULL,
                status ENUM('Ready', 'Uploaded', 'In Progress', 'New', 'Failed', 'Processing') NOT NULL DEFAULT 'New',
                created_by VARCHAR(36) NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
            )
            """,
            
            # Movie cast table
            """
            CREATE TABLE IF NOT EXISTS movie_cast (
                id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
                movie_id VARCHAR(36) NOT NULL,
                actor_name VARCHAR(255) NOT NULL,
                character_name VARCHAR(255) NULL,
                role_type ENUM('lead', 'supporting', 'cameo') NOT NULL DEFAULT 'supporting',
                order_index INT NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
            )
            """,
            
            # Content items table
            """
            CREATE TABLE IF NOT EXISTS content_items (
                id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
                name VARCHAR(255) NOT NULL,
                content_type ENUM('Movie', 'Reel', 'Trailer', 'Series', 'Documentary') NOT NULL,
                status ENUM('Ready', 'Uploaded', 'In Progress', 'New', 'Failed', 'Processing') NOT NULL DEFAULT 'New',
                priority ENUM('High', 'Medium', 'Low') NOT NULL DEFAULT 'Medium',
                description TEXT NULL,
                file_path TEXT NULL,
                file_size_bytes BIGINT NULL,
                duration_seconds INT NULL,
                thumbnail_url TEXT NULL,
                metadata JSON NULL,
                movie_id VARCHAR(36) NULL,
                created_by VARCHAR(36) NULL,
                uploaded_at TIMESTAMP NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE SET NULL,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
            )
            """,
            
            # Content tags table
            """
            CREATE TABLE IF NOT EXISTS content_tags (
                id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
                content_id VARCHAR(36) NOT NULL,
                tag_name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (content_id) REFERENCES content_items(id) ON DELETE CASCADE,
                UNIQUE KEY unique_content_tag (content_id, tag_name)
            )
            """,
            
            # Insert default admin user
            """
            INSERT IGNORE INTO users (id, username, email, password_hash, full_name, role, is_active) 
            VALUES ('admin-001', 'admin', 'admin@cinemitr.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj7VV5BVhqF.', 'CineMitr Administrator', 'admin', TRUE)
            """,
            
            # Insert sample movies
            """
            INSERT IGNORE INTO movies (id, title, genre, release_date, duration_minutes, description, director, rating, language, country, status, created_by) VALUES
            ('movie-001', '12th Fail', 'Drama', '2023-10-27', 147, 'Based on true events, about a man who overcomes extreme hardships', 'Vidhu Vinod Chopra', '8.9', 'Hindi', 'India', 'Ready', 'admin-001'),
            ('movie-002', 'Pathaan', 'Action', '2023-01-25', 146, 'An action thriller featuring a secret agent', 'Siddharth Anand', '7.2', 'Hindi', 'India', 'Uploaded', 'admin-001'),
            ('movie-003', 'Jawan', 'Action', '2023-09-07', 169, 'A high-octane action thriller', 'Atlee', '7.8', 'Hindi', 'India', 'Ready', 'admin-001')
            """,
            
            # Insert sample content
            """
            INSERT IGNORE INTO content_items (id, name, content_type, status, priority, description, file_size_bytes, duration_seconds, movie_id, created_by) VALUES
            ('content-001', '12th Fail Full Movie', 'Movie', 'Ready', 'High', 'Complete movie file', 2576588800, 8820, 'movie-001', 'admin-001'),
            ('content-002', '12th Fail Trailer', 'Trailer', 'Uploaded', 'Medium', 'Official trailer', 163840000, 180, 'movie-001', 'admin-001'),
            ('content-003', 'Pathaan Action Reel', 'Reel', 'Processing', 'Medium', 'Action sequence highlight', 52428800, 60, 'movie-002', 'admin-001')
            """
        ]
        
        with db_manager.get_session() as session:
            for i, statement in enumerate(sql_statements):
                try:
                    logger.info(f"Executing statement {i+1}/{len(sql_statements)}")
                    session.execute(text(statement))
                    session.commit()
                except Exception as e:
                    logger.error(f"Error executing statement {i+1}: {str(e)}")
                    if "already exists" not in str(e).lower() and "Duplicate entry" not in str(e):
                        raise
                    else:
                        logger.warning(f"Skipping existing object in statement {i+1}")
        
        logger.info("Simple database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False

def main():
    """Main function"""
    print("CineMitr Simple Database Initialization")
    print("=" * 40)
    
    if init_database_simple():
        print("Database initialized successfully!")
        return True
    else:
        print("Database initialization failed!")
        return False

if __name__ == "__main__":
    import sys
    
    success = main()
    sys.exit(0 if success else 1)