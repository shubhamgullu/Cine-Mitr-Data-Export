#!/usr/bin/env python3
"""
Database initialization script for CineMitr Content Management
This script initializes the database with tables and sample data
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def initialize_database():
    """Initialize database with tables and sample data"""
    try:
        # Import after loading environment variables
        from database.connection import db_manager
        from database.models import *  # Import all models
        
        print("🚀 Initializing CineMitr database...")
        
        # Initialize database connection
        db_manager.initialize()
        
        # Test connection
        if not db_manager.test_connection():
            print("❌ Database connection test failed!")
            return False
        
        print("✅ Database connection successful")
        
        # Create all tables
        db_manager.create_tables()
        print("✅ Database tables created successfully")
        
        # Add sample data (optional)
        add_sample_data = input("Do you want to add sample data? (y/N): ").lower().strip()
        if add_sample_data in ['y', 'yes']:
            create_sample_data()
        
        print("🎉 Database initialization completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    try:
        from database.connection import db_manager
        from database.models import Movie, ContentItem
        from datetime import datetime
        
        with db_manager.get_session() as session:
            # Create sample movies
            sample_movies = [
                {
                    "title": "Lakshya",
                    "genre": "Drama",
                    "director": "Farhan Akhtar",
                    "language": "Hindi",
                    "country": "India",
                    "description": "A story about finding one's purpose in life"
                },
                {
                    "title": "ZNMD",
                    "genre": "Adventure",
                    "director": "Zoya Akhtar", 
                    "language": "Hindi",
                    "country": "India",
                    "description": "Three friends embark on a bachelor trip to Spain"
                }
            ]
            
            created_movies = []
            for movie_data in sample_movies:
                existing_movie = session.query(Movie).filter(Movie.title == movie_data["title"]).first()
                if not existing_movie:
                    movie = Movie(**movie_data)
                    session.add(movie)
                    created_movies.append(movie)
            
            session.commit()
            
            # Create sample content items
            if created_movies:
                sample_content = [
                    {
                        "name": "Lakshya Training Scene",
                        "content_type": "Reel",
                        "status": "New",
                        "priority": "Medium",
                        "description": "Training scene from Lakshya movie",
                        "link_url": "https://www.instagram.com/reel/sample1",
                        "movie_name": "Lakshya",
                        "local_status": "Downloaded",
                        "edited_status": "Basic Crop",
                        "file_path": "D:\\CineMitr\\Reels Content\\Reels Data\\lakshya\\sample1"
                    },
                    {
                        "name": "ZNMD Adventure Clip",
                        "content_type": "Trailer",
                        "status": "Ready",
                        "priority": "High",
                        "description": "Adventure scenes from ZNMD",
                        "link_url": "https://www.instagram.com/reel/sample2",
                        "movie_name": "ZNMD",
                        "local_status": "Ready",
                        "edited_status": "Color Corrected",
                        "file_path": "D:\\CineMitr\\Reels Content\\Reels Data\\znmd\\sample2"
                    }
                ]
                
                for content_data in sample_content:
                    content = ContentItem(**content_data)
                    session.add(content)
                
                session.commit()
        
        print("✅ Sample data created successfully")
        
    except Exception as e:
        print(f"❌ Failed to create sample data: {str(e)}")

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
    print("🎬 CineMitr Database Initialization")
    print("==================================")
    
    # Check configuration first
    if not check_database_config():
        sys.exit(1)
    
    # Initialize database
    if initialize_database():
        print("\n🚀 You can now run the dashboard with: streamlit run cinemitr_dashboard.py")
    else:
        print("\n❌ Database initialization failed. Please check the error messages above.")
        sys.exit(1)