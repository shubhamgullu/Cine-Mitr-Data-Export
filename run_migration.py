#!/usr/bin/env python3
"""
Database migration script to add is_available and location columns to movies table
"""

import os
from database.connection import db_manager
from sqlalchemy import text

def run_migration():
    """Run the database migration"""
    try:
        print("Starting database migration...")
        
        # Initialize database connection
        db_manager.initialize()
        
        with db_manager.get_session() as session:
            # Add is_available column
            try:
                session.execute(text("""
                    ALTER TABLE movies 
                    ADD COLUMN is_available BOOLEAN NOT NULL DEFAULT TRUE 
                    COMMENT 'Whether the movie is available'
                """))
                print("[OK] Added is_available column")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("[INFO] is_available column already exists")
                else:
                    print(f"[ERROR] Error adding is_available column: {e}")
            
            # Add location column
            try:
                session.execute(text("""
                    ALTER TABLE movies 
                    ADD COLUMN location TEXT NULL 
                    COMMENT 'Local file path for the movie file'
                """))
                print("[OK] Added location column")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("[INFO] location column already exists")
                else:
                    print(f"[ERROR] Error adding location column: {e}")
            
            # Update existing movies to have default values
            try:
                result = session.execute(text("""
                    UPDATE movies SET is_available = TRUE WHERE is_available IS NULL
                """))
                print(f"[OK] Updated {result.rowcount} movies with default is_available value")
            except Exception as e:
                print(f"[ERROR] Error updating default values: {e}")
            
            # Create indexes for better performance
            try:
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_movies_is_available ON movies(is_available)
                """))
                print("[OK] Created index on is_available column")
            except Exception as e:
                print(f"[ERROR] Error creating is_available index: {e}")
            
            try:
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_movies_location ON movies(location(255))
                """))
                print("[OK] Created index on location column")
            except Exception as e:
                print(f"[ERROR] Error creating location index: {e}")
            
            # Commit all changes
            session.commit()
            print("[OK] Migration completed successfully!")
            
            # Verify the changes
            result = session.execute(text("DESCRIBE movies"))
            columns = result.fetchall()
            
            print("\n[INFO] Current movies table structure:")
            for column in columns:
                print(f"  - {column[0]}: {column[1]} ({column[2]})")
            
            # Check current movies data
            result = session.execute(text("""
                SELECT id, title, is_available, location FROM movies LIMIT 5
            """))
            movies = result.fetchall()
            
            print(f"\n[INFO] Sample movies data ({len(movies)} records):")
            for movie in movies:
                location_display = movie[3][:30] + "..." if movie[3] and len(movie[3]) > 30 else movie[3] or "N/A"
                print(f"  - {movie[1]}: Available={movie[2]}, Location={location_display}")
                
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("\n[SUCCESS] Database migration completed successfully!")
        print("The movies table now includes is_available and location columns.")
    else:
        print("\n[FAILED] Database migration failed. Please check the errors above.")