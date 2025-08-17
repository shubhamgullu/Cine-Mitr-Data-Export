#!/usr/bin/env python3
"""
Test script for database integration
"""

import asyncio
import os
from datetime import datetime
from database.connection import db_manager
from services.content_service import ContentService
from services.dashboard_service import DashboardService
from models import ContentCreateRequest, MovieCreateRequest, ContentType, Priority
from utils.logger import setup_logger

logger = setup_logger(__name__)

async def test_content_operations():
    """Test content CRUD operations"""
    logger.info("Testing content operations...")
    
    content_service = ContentService()
    await content_service.initialize()
    
    # Test create content
    logger.info("Creating test content...")
    content_data = ContentCreateRequest(
        name="Test Movie Content",
        content_type=ContentType.MOVIE,
        priority=Priority.HIGH,
        description="Test movie for database integration",
        tags=["test", "database", "integration"],
        metadata={"resolution": "1080p", "codec": "h264"}
    )
    
    created_content = await content_service.create_content(content_data)
    logger.info(f"Created content: {created_content.id} - {created_content.name}")
    
    # Test get content by ID
    logger.info("Retrieving content by ID...")
    retrieved_content = await content_service.get_content_by_id(created_content.id)
    if retrieved_content:
        logger.info(f"Retrieved content: {retrieved_content.name}")
    else:
        logger.error("Failed to retrieve content")
        return False
    
    # Test content list
    logger.info("Getting content list...")
    from models import ContentFilters
    filters = ContentFilters()
    content_list = await content_service.get_content_list(1, 10, filters)
    logger.info(f"Content list contains {len(content_list.items)} items")
    
    # Test update content
    logger.info("Updating content...")
    from models import ContentUpdateRequest
    update_data = ContentUpdateRequest(
        description="Updated test movie description"
    )
    updated_content = await content_service.update_content(created_content.id, update_data)
    if updated_content:
        logger.info(f"Updated content description: {updated_content.description}")
    
    # Test delete content
    logger.info("Deleting test content...")
    delete_result = await content_service.delete_content(created_content.id)
    if delete_result:
        logger.info("Successfully deleted test content")
    else:
        logger.error("Failed to delete test content")
        return False
    
    return True

async def test_movie_operations():
    """Test movie CRUD operations"""
    logger.info("Testing movie operations...")
    
    content_service = ContentService()
    
    # Test create movie
    logger.info("Creating test movie...")
    movie_data = MovieCreateRequest(
        title="Test Database Movie",
        genre="Action",
        duration_minutes=120,
        description="Test movie for database integration",
        director="Test Director",
        cast=["Actor 1", "Actor 2"],
        rating="8.5",
        language="English"
    )
    
    created_movie = await content_service.create_movie(movie_data)
    logger.info(f"Created movie: {created_movie.id} - {created_movie.title}")
    
    # Test get movie by ID
    logger.info("Retrieving movie by ID...")
    retrieved_movie = await content_service.get_movie_by_id(created_movie.id)
    if retrieved_movie:
        logger.info(f"Retrieved movie: {retrieved_movie.title}")
    else:
        logger.error("Failed to retrieve movie")
        return False
    
    # Test movie list
    logger.info("Getting movie list...")
    from models import MovieFilters
    filters = MovieFilters()
    movie_list = await content_service.get_movies_list(1, 10, filters)
    logger.info(f"Movie list contains {len(movie_list.items)} items")
    
    # Test delete movie
    logger.info("Deleting test movie...")
    delete_result = await content_service.delete_movie(created_movie.id)
    if delete_result:
        logger.info("Successfully deleted test movie")
    else:
        logger.error("Failed to delete test movie")
        return False
    
    return True

async def test_dashboard_operations():
    """Test dashboard operations"""
    logger.info("Testing dashboard operations...")
    
    dashboard_service = DashboardService()
    await dashboard_service.initialize()
    
    # Test dashboard metrics
    logger.info("Getting dashboard metrics...")
    metrics = await dashboard_service.get_metrics()
    logger.info(f"Dashboard metrics: {metrics.total_movies} movies, {metrics.content_items} content items")
    
    # Test status distribution
    logger.info("Getting status distribution...")
    status_dist = await dashboard_service.get_status_distribution()
    logger.info(f"Status distribution: Ready={status_dist.ready}, Uploaded={status_dist.uploaded}")
    
    # Test priority distribution
    logger.info("Getting priority distribution...")
    priority_dist = await dashboard_service.get_priority_distribution()
    logger.info(f"Priority distribution: High={priority_dist.high}, Medium={priority_dist.medium}, Low={priority_dist.low}")
    
    # Test recent activity
    logger.info("Getting recent activity...")
    recent_activity = await dashboard_service.get_recent_activity(5)
    logger.info(f"Recent activity contains {len(recent_activity)} items")
    
    return True

async def main():
    """Main test function"""
    print("CineMitr Database Integration Test")
    print("=" * 40)
    
    try:
        # Initialize database connection
        logger.info("Initializing database connection...")
        db_manager.initialize()
        
        # Test connection
        if not db_manager.test_connection():
            logger.error("Database connection test failed")
            print("❌ Database connection failed!")
            return False
        
        logger.info("Database connection successful")
        print("✅ Database connection successful!")
        
        # Run tests
        tests = [
            ("Content Operations", test_content_operations()),
            ("Movie Operations", test_movie_operations()),
            ("Dashboard Operations", test_dashboard_operations())
        ]
        
        for test_name, test_coro in tests:
            print(f"\n🧪 Running {test_name}...")
            try:
                result = await test_coro
                if result:
                    print(f"✅ {test_name} passed!")
                else:
                    print(f"❌ {test_name} failed!")
                    return False
            except Exception as e:
                logger.error(f"{test_name} failed with error: {str(e)}")
                print(f"❌ {test_name} failed with error: {str(e)}")
                return False
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        print(f"❌ Test execution failed: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)