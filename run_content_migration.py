#!/usr/bin/env python3
"""
Database migration script to add new content management columns
This script adds the new fields to the content_items table
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import text

# Load environment variables
load_dotenv()

def run_content_migration():
    """Run the content management database migration"""
    try:
        # Import after loading environment variables
        from database.connection import db_manager
        
        print("🚀 Running content management database migration...")
        
        # Initialize database connection
        db_manager.initialize()
        
        # Test connection
        if not db_manager.test_connection():
            print("❌ Database connection test failed!")
            return False
        
        print("✅ Database connection successful")
        
        # Run migration SQL commands
        migration_commands = [
            # Add new columns to content_items table
            """
            ALTER TABLE content_items 
            ADD COLUMN link_url TEXT COMMENT 'Original source URL (e.g., Instagram reel URL)'
            """,
            """
            ALTER TABLE content_items 
            ADD COLUMN movie_name VARCHAR(255) COMMENT 'Movie name for content association'
            """,
            """
            ALTER TABLE content_items 
            ADD COLUMN edited_status VARCHAR(100) DEFAULT 'Pending' COMMENT 'Edit status (Basic Crop, etc.)'
            """,
            """
            ALTER TABLE content_items 
            ADD COLUMN content_to_add TEXT COMMENT 'Notes about content editing needs'
            """,
            """
            ALTER TABLE content_items 
            ADD COLUMN source_folder TEXT COMMENT 'Source folder path for downloaded content'
            """,
            """
            ALTER TABLE content_items 
            ADD COLUMN local_status ENUM('Downloaded', 'Processing', 'Ready', 'Failed', 'Pending') DEFAULT 'Pending'
            """,
            # Add indexes for better performance
            """
            CREATE INDEX idx_content_items_movie_name ON content_items(movie_name)
            """,
            """
            CREATE INDEX idx_content_items_local_status ON content_items(local_status)
            """,
            """
            CREATE INDEX idx_content_items_edited_status ON content_items(edited_status)
            """,
            """
            CREATE INDEX idx_content_items_link_url ON content_items(link_url(255))
            """,
            # Add index on movies table for autocomplete
            """
            CREATE INDEX idx_movies_title_search ON movies(title)
            """,
            # Update existing records with default values
            """
            UPDATE content_items 
            SET edited_status = 'Pending' 
            WHERE edited_status IS NULL
            """,
            """
            UPDATE content_items 
            SET local_status = 'Pending' 
            WHERE local_status IS NULL
            """
        ]
        
        with db_manager.get_session() as session:
            success_count = 0
            for i, command in enumerate(migration_commands, 1):
                try:
                    print(f"📝 Running migration step {i}/{len(migration_commands)}...")
                    session.execute(text(command.strip()))
                    success_count += 1
                    print(f"   ✅ Step {i} completed")
                except Exception as e:
                    error_msg = str(e)
                    if "Duplicate column name" in error_msg or "already exists" in error_msg:
                        print(f"   ⚠️  Step {i} skipped (column/index already exists)")
                        success_count += 1
                    elif "Duplicate key name" in error_msg:
                        print(f"   ⚠️  Step {i} skipped (index already exists)")
                        success_count += 1
                    else:
                        print(f"   ❌ Step {i} failed: {error_msg}")
            
            session.commit()
        
        print(f"\n🎉 Migration completed! {success_count}/{len(migration_commands)} steps successful")
        
        # Verify the new columns exist
        print("🔍 Verifying new columns...")
        verify_migration()
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

def verify_migration():
    """Verify that the migration was successful"""
    try:
        from database.connection import db_manager
        
        with db_manager.get_session() as session:
            # Check if new columns exist
            result = session.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'content_items' 
                AND COLUMN_NAME IN ('link_url', 'movie_name', 'edited_status', 'content_to_add', 'source_folder', 'local_status')
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            expected_columns = ['link_url', 'movie_name', 'edited_status', 'content_to_add', 'source_folder', 'local_status']
            
            missing_columns = [col for col in expected_columns if col not in existing_columns]
            
            if not missing_columns:
                print("✅ All new columns verified successfully")
                return True
            else:
                print(f"❌ Missing columns: {', '.join(missing_columns)}")
                return False
                
    except Exception as e:
        print(f"⚠️  Column verification failed: {str(e)}")
        print("💡 This might be normal if using a non-MySQL database")
        return True  # Don't fail the migration for this

def check_database_config():
    """Check if database configuration is valid"""
    required_vars = ["DATABASE_HOST", "DATABASE_NAME", "DATABASE_USER"]
    missing_vars = []
    
    print("🔍 Checking database configuration...")
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("💡 Please create a .env file with the following variables:")
        print("DATABASE_HOST=localhost")
        print("DATABASE_PORT=3306")
        print("DATABASE_NAME=cinemitr_db")
        print("DATABASE_USER=root")
        print("DATABASE_PASSWORD=your_password")
        print("DATABASE_DRIVER=mysql+pymysql")
        return False
    
    print("✅ Database configuration looks good")
    return True

if __name__ == "__main__":
    print("🎬 CineMitr Content Management Migration")
    print("=======================================")
    
    # Check configuration first
    if not check_database_config():
        sys.exit(1)
    
    # Run migration
    if run_content_migration():
        print("\n🚀 Migration completed successfully!")
        print("💡 You can now run the dashboard with updated content management features.")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)