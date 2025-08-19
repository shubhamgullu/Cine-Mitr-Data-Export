import requests
import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime
from config import DashboardConfig
from models import (
    DashboardMetrics, StatusDistribution, PriorityDistribution, 
    ContentItem, ContentStatus, Priority, ContentType
)

class APIService:
    def __init__(self, config: DashboardConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    @st.cache_data(ttl=30)
    def get_dashboard_metrics(_self) -> DashboardMetrics:
        """Fetch dashboard metrics from database"""
        try:
            from database.connection import db_manager
            from database.repository import AnalyticsRepository
            
            with db_manager.get_session() as session:
                analytics_repo = AnalyticsRepository(session)
                metrics_data = analytics_repo.get_dashboard_metrics()
                
                return DashboardMetrics(
                    total_movies=metrics_data.get('total_movies', 0),
                    content_items=metrics_data.get('content_items', 0),
                    uploaded=metrics_data.get('uploaded', 0),
                    uploaded_weekly_change=metrics_data.get('uploaded_weekly_change', 0),
                    pending=metrics_data.get('pending', 0),
                    upload_rate=metrics_data.get('upload_rate', 0.0),
                    storage_used_gb=metrics_data.get('storage_used_gb', 0.0),
                    storage_total_gb=metrics_data.get('storage_total_gb', 1000.0),
                    active_uploads=metrics_data.get('active_uploads', 0),
                    failed_uploads=metrics_data.get('failed_uploads', 0)
                )
        except Exception as e:
            error_msg = str(e)
            if "Unknown column" in error_msg or "doesn't exist" in error_msg:
                st.warning("⚠️ Database schema needs to be updated. Please run the migration script.")
                st.info("💡 Run: `python run_content_migration.py` to update your database schema.")
            else:
                st.error(f"Error fetching metrics: {error_msg}")
            return DashboardMetrics(
                total_movies=0, content_items=0, uploaded=0, uploaded_weekly_change=0,
                pending=0, upload_rate=0.0, storage_used_gb=0.0, storage_total_gb=1000.0,
                active_uploads=0, failed_uploads=0
            )
    
    @st.cache_data(ttl=30)
    def get_status_distribution(_self) -> StatusDistribution:
        """Fetch content status distribution from database"""
        try:
            from database.connection import db_manager
            from database.repository import AnalyticsRepository
            
            with db_manager.get_session() as session:
                analytics_repo = AnalyticsRepository(session)
                distribution_data = analytics_repo.get_status_distribution()
                
                return StatusDistribution(
                    ready=distribution_data.get('ready', 0),
                    uploaded=distribution_data.get('uploaded', 0),
                    in_progress=distribution_data.get('in_progress', 0),
                    new=distribution_data.get('new', 0)
                )
        except Exception as e:
            st.error(f"Error fetching status distribution: {str(e)}")
            return StatusDistribution(0, 0, 0, 0)
    
    @st.cache_data(ttl=30)
    def get_priority_distribution(_self) -> PriorityDistribution:
        """Fetch priority distribution from database"""
        try:
            from database.connection import db_manager
            from database.repository import AnalyticsRepository
            
            with db_manager.get_session() as session:
                analytics_repo = AnalyticsRepository(session)
                distribution_data = analytics_repo.get_priority_distribution()
                
                return PriorityDistribution(
                    high=distribution_data.get('high', 0),
                    medium=distribution_data.get('medium', 0),
                    low=distribution_data.get('low', 0)
                )
        except Exception as e:
            st.error(f"Error fetching priority distribution: {str(e)}")
            return PriorityDistribution(0, 0, 0)
    
    @st.cache_data(ttl=30)
    def get_recent_activity(_self, limit: int = 10) -> List[ContentItem]:
        """Fetch recent activity from database"""
        try:
            from database.connection import db_manager
            from database.repository import ContentRepository
            
            with db_manager.get_session() as session:
                content_repo = ContentRepository(session)
                db_content_list = content_repo.get_recent_activity(limit)
                
                activities = []
                for db_content in db_content_list:
                    activity = ContentItem(
                        id=db_content.id,
                        name=db_content.name,
                        content_type=ContentType(db_content.content_type),
                        status=ContentStatus(db_content.status),
                        priority=Priority(db_content.priority),
                        created_at=db_content.created_at,
                        updated_at=db_content.updated_at
                    )
                    activities.append(activity)
                
                return activities
        except Exception as e:
            st.error(f"Error fetching recent activity: {str(e)}")
            return []
    
    def refresh_data(self) -> bool:
        """Refresh all cached data"""
        try:
            # Clear Streamlit cache
            st.cache_data.clear()
            return True
        except Exception as e:
            st.error(f"Error refreshing data: {str(e)}")
            return False
    
    def import_data(self, file_data: bytes, file_type: str) -> Dict:
        """Import data via API"""
        try:
            # files = {'file': (f'import.{file_type}', file_data, f'application/{file_type}')}
            # response = self.session.post(f"{self.config.API_BASE_URL}/import", files=files)
            # response.raise_for_status()
            # return response.json()
            
            # Mock response
            return {"status": "success", "message": "Data imported successfully", "imported_count": 25}
        except Exception as e:
            st.error(f"Error importing data: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def add_content(self, content_data: Dict) -> Dict:
        """Add new content via API"""
        try:
            # response = self.session.post(f"{self.config.API_BASE_URL}/content", json=content_data)
            # response.raise_for_status()
            # return response.json()
            
            # Mock response
            return {"status": "success", "message": "Content added successfully", "id": "new_123"}
        except Exception as e:
            st.error(f"Error adding content: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def update_content_status(self, content_id: str, status: ContentStatus) -> Dict:
        """Update content status via API"""
        try:
            # response = self.session.patch(
            #     f"{self.config.API_BASE_URL}/content/{content_id}/status", 
            #     json={"status": status.value}
            # )
            # response.raise_for_status()
            # return response.json()
            
            # Mock response
            return {"status": "success", "message": f"Content {content_id} status updated to {status.value}"}
        except Exception as e:
            st.error(f"Error updating content status: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def delete_content(self, content_id: str) -> Dict:
        """Delete content via API"""
        try:
            # response = self.session.delete(f"{self.config.API_BASE_URL}/content/{content_id}")
            # response.raise_for_status()
            # return response.json()
            
            # Mock response
            return {"status": "success", "message": f"Content {content_id} deleted successfully"}
        except Exception as e:
            st.error(f"Error deleting content: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def create_movie(self, movie_data: Dict) -> Dict:
        """Create new movie via API"""
        try:
            response = self.session.post(f"{self.config.api.base_url}/movies", json=movie_data)
            response.raise_for_status()
            api_response = response.json()
            
            if api_response.get("success"):
                return {
                    "status": "success", 
                    "message": api_response.get("message", "Movie created successfully"),
                    "data": api_response.get("data", {})
                }
            else:
                return {
                    "status": "error", 
                    "message": api_response.get("message", "Failed to create movie")
                }
        except Exception as e:
            st.error(f"Error creating movie: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_movies_list(self, page: int = 1, limit: int = 20, search: str = None, 
                       genre: str = None, status: str = None, language: str = None, 
                       release_year: int = None) -> List[Dict]:
        """Get movies list from database with search and filtering capabilities"""
        try:
            from database.connection import db_manager
            from database.repository import MovieRepository
            from models import MovieFilters
            
            with db_manager.get_session() as session:
                movie_repo = MovieRepository(session)
                filters = MovieFilters(
                    search=search,
                    genre=genre,
                    status=status,
                    language=language,
                    release_year=release_year
                )
                movies, total_count = movie_repo.get_list(page, limit, filters)
                
                # Convert SQLAlchemy models to dictionaries
                movies_data = []
                for movie in movies:
                    movie_dict = {
                        'id': movie.id,
                        'title': movie.title,
                        'genre': movie.genre,
                        'duration_minutes': movie.duration_minutes,
                        'duration': movie.duration_minutes,  # For backward compatibility
                        'status': movie.status,
                        'is_available': movie.is_available,
                        'location': movie.location,
                        'release_date': movie.release_date.isoformat() if movie.release_date else None,
                        'director': movie.director,
                        'description': movie.description,
                        'language': movie.language,
                        'country': movie.country,
                        'rating': movie.rating,
                        'created_at': movie.created_at.isoformat() if movie.created_at else None,
                        'updated_at': movie.updated_at.isoformat() if movie.updated_at else None
                    }
                    movies_data.append(movie_dict)
                
                return movies_data
                
        except Exception as e:
            st.error(f"Error fetching movies from database: {str(e)}")
            return []
    
    def export_movies(self, format: str = "csv", selected_ids: List[str] = None) -> Dict:
        """Export movies to specified format"""
        try:
            # Start the export process
            response = self.session.get(f"{self.config.api.base_url}/export/{format}")
            response.raise_for_status()
            api_response = response.json()
            
            if api_response.get("success"):
                return {
                    "status": "success",
                    "export_id": api_response.get("export_id"),
                    "message": api_response.get("message", f"Export to {format.upper()} started")
                }
            else:
                return {
                    "status": "error",
                    "message": api_response.get("message", "Export failed")
                }
                
        except Exception as e:
            st.error(f"Error starting export: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def download_export_file(self, export_id: str) -> bytes:
        """Download exported file by export ID"""
        try:
            response = self.session.get(f"{self.config.api.base_url}/download/{export_id}")
            response.raise_for_status()
            return response.content
        except Exception as e:
            st.error(f"Error downloading file: {str(e)}")
            return None
    
    def bulk_import_movies_from_file(self, file_content: bytes, filename: str, operation: str = "upsert") -> Dict:
        """Bulk import movies from uploaded file"""
        try:
            # Prepare the file for upload
            files = {
                'file': (filename, file_content, self._get_content_type(filename))
            }
            
            # Use a fresh requests session for file upload to avoid header conflicts
            import requests
            response = requests.post(
                f"{self.config.api.base_url}/movies/bulk-import/file?operation={operation}",
                files=files
            )
            response.raise_for_status()
            api_response = response.json()
            
            if api_response.get("success"):
                return {
                    "status": "success",
                    "data": api_response.get("data", {}),
                    "message": api_response.get("message", "Bulk import completed successfully")
                }
            else:
                return {
                    "status": "error",
                    "message": api_response.get("message", "Bulk import failed")
                }
                
        except Exception as e:
            st.error(f"Error in bulk import: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def download_movie_template(self, template_type: str = "csv") -> bytes:
        """Download movie bulk import template"""
        try:
            response = self.session.get(f"{self.config.api.base_url}/movies/templates/download/{template_type}")
            response.raise_for_status()
            return response.content
        except Exception as e:
            st.error(f"Error downloading template: {str(e)}")
            return None
    
    @st.cache_data(ttl=60)
    def get_storage_stats(_self) -> Dict:
        """Get storage statistics from database"""
        try:
            from database.connection import db_manager
            from database.repository import AnalyticsRepository
            
            with db_manager.get_session() as session:
                analytics_repo = AnalyticsRepository(session)
                storage_stats = analytics_repo.get_storage_stats()
                return storage_stats
        except Exception as e:
            st.error(f"Error fetching storage stats: {str(e)}")
            return {
                'total_size_gb': 0,
                'used_size_gb': 0,
                'available_size_gb': 1000,
                'usage_percentage': 0,
                'file_count': 0,
                'largest_files': []
            }
    
    @st.cache_data(ttl=60)
    def get_storage_by_type(_self) -> Dict:
        """Get storage breakdown by content type"""
        try:
            from database.connection import db_manager
            from database.repository import AnalyticsRepository
            from sqlalchemy import func
            from database.models import ContentItem
            
            with db_manager.get_session() as session:
                # Get storage by content type
                content_stats = session.query(
                    ContentItem.content_type,
                    func.sum(ContentItem.file_size_bytes).label('total_bytes')
                ).filter(
                    ContentItem.file_size_bytes.isnot(None)
                ).group_by(ContentItem.content_type).all()
                
                # Convert to GB and create the result
                storage_by_type = {}
                for content_type, total_bytes in content_stats:
                    storage_by_type[content_type] = round((total_bytes or 0) / (1024 ** 3), 2)
                
                # Fill in missing types with 0
                types = ['Movie', 'Reel', 'Trailer', 'Series', 'Documentary']
                for content_type in types:
                    if content_type not in storage_by_type:
                        storage_by_type[content_type] = 0
                
                return storage_by_type
                
        except Exception as e:
            st.error(f"Error fetching storage by type: {str(e)}")
            return {
                'Movie': 450,
                'Reel': 150, 
                'Trailer': 60,
                'Series': 20,
                'Documentary': 10
            }

    def _get_content_type(self, filename: str) -> str:
        """Get content type based on file extension"""
        ext = filename.split('.')[-1].lower() if filename else ""
        content_types = {
            "csv": "text/csv",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xls": "application/vnd.ms-excel",
            "json": "application/json"
        }
        return content_types.get(ext, "application/octet-stream")
    
    def create_content_item(self, content_data: Dict) -> Dict:
        """Create new content item via database"""
        try:
            from database.connection import db_manager
            from database.repository import ContentRepository
            
            with db_manager.get_session() as session:
                content_repo = ContentRepository(session)
                
                # Create the content item
                db_content = content_repo.create(content_data)
                session.commit()
                
                return {
                    "status": "success", 
                    "message": "Content item created successfully",
                    "data": {
                        "id": db_content.id,
                        "name": db_content.name
                    }
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_content_items_list(self, page: int = 1, limit: int = 50, search: str = None, 
                              status: str = None, content_type: str = None, priority: str = None) -> List[Dict]:
        """Get content items list from database with filtering"""
        try:
            from database.connection import db_manager
            from database.repository import ContentRepository
            from models import ContentFilters
            
            with db_manager.get_session() as session:
                content_repo = ContentRepository(session)
                
                # Create filters
                filters = ContentFilters(
                    search=search,
                    status=status,
                    content_type=content_type,
                    priority=priority
                )
                
                content_items, total_count = content_repo.get_list(page, limit, filters)
                
                # Convert SQLAlchemy models to dictionaries
                content_data = []
                for content in content_items:
                    content_dict = {
                        'id': content.id,
                        'name': content.name,
                        'content_type': content.content_type,
                        'status': content.status,
                        'priority': content.priority,
                        'description': content.description,
                        'file_path': content.file_path,
                        'file_size_bytes': content.file_size_bytes,
                        'duration_seconds': content.duration_seconds,
                        'thumbnail_url': content.thumbnail_url,
                        'video_url': content.video_url,
                        'metadata': content.meta_data,
                        'movie_id': content.movie_id,
                        'uploaded_at': content.uploaded_at.isoformat() if content.uploaded_at else None,
                        'created_at': content.created_at.isoformat() if content.created_at else None,
                        'updated_at': content.updated_at.isoformat() if content.updated_at else None,
                        # New fields (with safe attribute access)
                        'link_url': getattr(content, 'link_url', None),
                        'movie_name': getattr(content, 'movie_name', None),
                        'local_status': getattr(content, 'local_status', 'Pending'),
                        'edited_status': getattr(content, 'edited_status', 'Pending'),
                        'content_to_add': getattr(content, 'content_to_add', None),
                        'source_folder': getattr(content, 'source_folder', None),
                        'location_path': getattr(content, 'source_folder', content.file_path) if hasattr(content, 'source_folder') else content.file_path
                    }
                    content_data.append(content_dict)
                
                return content_data
                
        except Exception as e:
            error_msg = str(e)
            if "Unknown column" in error_msg or "doesn't exist" in error_msg:
                st.warning("⚠️ Database schema needs to be updated for full content management features.")
                
                # Show migration button in the error message
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("🚀 Run Migration Now", key="content_migration_btn", type="primary"):
                        try:
                            import subprocess
                            import sys
                            with st.spinner("🔄 Running migration..."):
                                result = subprocess.run(
                                    [sys.executable, "run_content_migration.py"],
                                    capture_output=True,
                                    text=True
                                )
                                if result.returncode == 0:
                                    st.success("✅ Migration completed! Please refresh the page.")
                                    st.balloons()
                                else:
                                    st.error(f"Migration failed: {result.stderr}")
                        except Exception as me:
                            st.error(f"Failed to run migration: {str(me)}")
                
                st.info("💡 Or run manually: `python run_content_migration.py`")
            else:
                st.error(f"Error fetching content items from database: {error_msg}")
            return []
    
    def delete_content_item(self, content_id: str) -> Dict:
        """Delete content item from database"""
        try:
            from database.connection import db_manager
            from database.repository import ContentRepository
            
            with db_manager.get_session() as session:
                content_repo = ContentRepository(session)
                
                success = content_repo.delete(content_id)
                if success:
                    session.commit()
                    return {"status": "success", "message": "Content item deleted successfully"}
                else:
                    return {"status": "error", "message": "Content item not found"}
                    
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_movie_names_autocomplete(self, search_term: str = "") -> List[str]:
        """Get movie names for autocomplete based on search term"""
        try:
            from database.connection import db_manager
            from database.repository import MovieRepository
            from database.models import Movie
            
            with db_manager.get_session() as session:
                # First, get total count of movies
                total_movies = session.query(Movie).count()
                
                if total_movies == 0:
                    # No movies in database, create sample movies automatically
                    success = self._create_sample_movies()
                    if success:
                        # Re-query after creating sample movies
                        total_movies = session.query(Movie).count()
                    else:
                        return []
                
                query = session.query(Movie.title).distinct()
                
                if search_term and len(search_term.strip()) >= 1:
                    # Use case-insensitive search
                    search_pattern = f"%{search_term.strip()}%"
                    query = query.filter(Movie.title.ilike(search_pattern))
                
                # Get first 10 matches
                results = query.limit(10).all()
                movie_names = [result[0] for result in results if result[0]]
                
                return movie_names
                
        except Exception as e:
            # Log error but don't expose to UI
            import logging
            logging.error(f"Error in get_movie_names_autocomplete: {str(e)}")
            return []
    
    def update_content_item(self, content_id: str, content_data: Dict) -> Dict:
        """Update content item via database"""
        try:
            from database.connection import db_manager
            from database.repository import ContentRepository
            
            with db_manager.get_session() as session:
                content_repo = ContentRepository(session)
                
                # Update the content item
                updated_content = content_repo.update(content_id, content_data)
                if updated_content:
                    session.commit()
                    return {
                        "status": "success", 
                        "message": "Content item updated successfully",
                        "data": {
                            "id": updated_content.id,
                            "name": updated_content.name
                        }
                    }
                else:
                    return {"status": "error", "message": "Content item not found"}
                    
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _create_sample_movies(self) -> bool:
        """Create sample movies for testing autocomplete"""
        try:
            from database.connection import db_manager
            from database.repository import MovieRepository
            from database.models import Movie
            
            sample_movies = [
                {
                    "title": "Lakshya",
                    "genre": "Drama",
                    "director": "Farhan Akhtar",
                    "language": "Hindi",
                    "country": "India",
                    "status": "Ready",
                    "description": "A story about finding one's purpose in life"
                },
                {
                    "title": "ZNMD",
                    "genre": "Adventure", 
                    "director": "Zoya Akhtar",
                    "language": "Hindi",
                    "country": "India",
                    "status": "Ready",
                    "description": "Three friends embark on a bachelor trip to Spain"
                },
                {
                    "title": "3 Idiots",
                    "genre": "Comedy",
                    "director": "Rajkumar Hirani",
                    "language": "Hindi",
                    "country": "India", 
                    "status": "Ready",
                    "description": "Comedy-drama about friendship and following your passion"
                },
                {
                    "title": "Dangal",
                    "genre": "Biography",
                    "director": "Nitesh Tiwari",
                    "language": "Hindi",
                    "country": "India",
                    "status": "Ready",
                    "description": "Biography of wrestler Mahavir Singh Phogat"
                },
                {
                    "title": "Queen",
                    "genre": "Comedy",
                    "director": "Vikas Bahl",
                    "language": "Hindi",
                    "country": "India",
                    "status": "Ready",
                    "description": "A woman goes on her honeymoon alone"
                }
            ]
            
            with db_manager.get_session() as session:
                movie_repo = MovieRepository(session)
                added_count = 0
                
                for movie_data in sample_movies:
                    try:
                        # Check if movie already exists
                        existing_movie = session.query(Movie).filter(Movie.title == movie_data["title"]).first()
                        if not existing_movie:
                            movie_repo.create(movie_data)
                            added_count += 1
                    except Exception as movie_error:
                        # Continue with other movies if one fails
                        continue
                
                if added_count > 0:
                    session.commit()
                
                return True
                
        except Exception as e:
            import logging
            logging.error(f"Error creating sample movies: {str(e)}")
            return False
    
    def export_content_items(self, format: str = "csv", selected_ids: List[str] = None) -> Dict:
        """Export content items to specified format"""
        try:
            # This would typically integrate with your export service
            # For now, return a mock response
            return {
                "status": "success",
                "export_id": "content_export_123",
                "message": f"Content items export to {format.upper()} started successfully"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}