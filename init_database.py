#!/usr/bin/env python3
"""
Database initialization script for CineMitr
This script creates the database tables and populates initial data
"""

import os
import sys
from sqlalchemy import text
from database.connection import db_manager
from utils.logger import setup_logger

logger = setup_logger(__name__)

def read_sql_file(file_path: str) -> str:
    """Read SQL file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"SQL file not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading SQL file {file_path}: {str(e)}")
        raise

def execute_sql_script(sql_content: str):
    """Execute SQL script with proper statement separation"""
    try:
        # Split the SQL content into individual statements
        statements = []
        current_statement = []
        in_delimiter_block = False
        
        for line in sql_content.split('\n'):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('--'):
                continue
            
            # Handle DELIMITER changes
            if line.startswith('DELIMITER'):
                if 'DELIMITER //' in line:
                    in_delimiter_block = True
                elif 'DELIMITER ;' in line:
                    in_delimiter_block = False
                    if current_statement:
                        statements.append('\n'.join(current_statement))
                        current_statement = []
                continue
            
            current_statement.append(line)
            
            # If not in delimiter block and line ends with semicolon, it's end of statement
            if not in_delimiter_block and line.endswith(';'):
                statements.append('\n'.join(current_statement))
                current_statement = []
        
        # Add any remaining statement
        if current_statement:
            statements.append('\n'.join(current_statement))
        
        # Execute each statement
        with db_manager.get_session() as session:
            for i, statement in enumerate(statements):
                statement = statement.strip()
                if not statement:
                    continue
                
                try:
                    logger.info(f"Executing statement {i+1}/{len(statements)}")
                    session.execute(text(statement))
                    session.commit()
                except Exception as e:
                    logger.error(f"Error executing statement {i+1}: {str(e)}")
                    logger.error(f"Statement: {statement[:200]}...")
                    session.rollback()
                    if "already exists" not in str(e).lower():
                        raise
                    else:
                        logger.warning(f"Skipping existing object in statement {i+1}")
        
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Error executing SQL script: {str(e)}")
        raise

def init_database():
    """Initialize the database with schema and data"""
    try:
        logger.info("Starting database initialization...")
        
        # Initialize database connection
        db_manager.initialize()
        
        # Test connection
        if not db_manager.test_connection():
            logger.error("Database connection test failed")
            return False
        
        logger.info("Database connection successful")
        
        # Read and execute the schema file
        schema_file = os.path.join(os.path.dirname(__file__), 'database_schema.sql')
        if not os.path.exists(schema_file):
            logger.error(f"Schema file not found: {schema_file}")
            return False
        
        logger.info("Reading database schema...")
        sql_content = read_sql_file(schema_file)
        
        logger.info("Executing database schema...")
        execute_sql_script(sql_content)
        
        logger.info("Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False

def main():
    """Main function"""
    print("CineMitr Database Initialization")
    print("=" * 40)
    
    if init_database():
        print("✅ Database initialized successfully!")
        sys.exit(0)
    else:
        print("❌ Database initialization failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()