"""
Content management service for handling content-related operations
"""

import asyncio
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models import (
    ContentItem as ContentItemModel, Movie as MovieModel, ContentCreateRequest, ContentUpdateRequest,
    ContentFilters, MovieFilters, ContentListResult, MoviesListResult,
    PaginationInfo, ContentStatus, Priority, ContentType, BulkUpdateResult
)
from database.connection import db_manager
from database.repository import (
    ContentRepository, MovieRepository, ContentTagRepository, 
    MovieCastRepository, AnalyticsRepository
)
from database.models import ContentItem, Movie, ContentTag, MovieCast
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ContentService:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300

    async def initialize(self):
        """Initialize the content service"""
        logger.info("Initializing Content Service with database connection")
        # Database tables are created via the schema migration
        # No need to populate sample data as it's in the SQL file

    def _convert_db_content_to_model(self, db_content: ContentItem) -> ContentItemModel:
        """Convert database ContentItem to Pydantic model"""
        tags = [tag.tag_name for tag in db_content.tags] if db_content.tags else []
        
        return ContentItemModel(
            id=db_content.id,
            name=db_content.name,
            content_type=ContentType(db_content.content_type),
            status=ContentStatus(db_content.status),
            priority=Priority(db_content.priority),
            description=db_content.description,
            file_path=db_content.file_path,
            file_size_bytes=db_content.file_size_bytes,
            duration_seconds=db_content.duration_seconds,
            thumbnail_url=db_content.thumbnail_url,
            metadata=db_content.meta_data,
            tags=tags,
            created_at=db_content.created_at,
            updated_at=db_content.updated_at,
            created_by=db_content.created_by,
            uploaded_at=db_content.uploaded_at
        )
    
    def _convert_db_movie_to_model(self, db_movie: Movie) -> MovieModel:
        """Convert database Movie to Pydantic model"""
        cast = [cast_member.actor_name for cast_member in db_movie.cast_members] if db_movie.cast_members else []
        
        return MovieModel(
            id=db_movie.id,
            title=db_movie.title,
            genre=db_movie.genre,
            release_date=db_movie.release_date,
            duration_minutes=db_movie.duration_minutes,
            description=db_movie.description,
            director=db_movie.director,
            cast=cast,
            rating=db_movie.rating,
            language=db_movie.language,
            country=db_movie.country,
            poster_url=db_movie.poster_url,
            trailer_url=db_movie.trailer_url,
            status=ContentStatus(db_movie.status),
            is_available=db_movie.is_available,
            location=db_movie.location,
            created_at=db_movie.created_at,
            updated_at=db_movie.updated_at
        )

    async def get_content_list(
        self, 
        page: int, 
        limit: int, 
        filters: ContentFilters
    ) -> ContentListResult:
        """Get paginated content list with filtering"""
        with db_manager.get_session() as session:
            content_repo = ContentRepository(session)
            db_content_list, total_count = content_repo.get_list(page, limit, filters)
            
            # Convert to Pydantic models
            content_items = [self._convert_db_content_to_model(db_content) for db_content in db_content_list]
            
            # Calculate pagination
            total_pages = (total_count + limit - 1) // limit
            
            pagination = PaginationInfo(
                page=page,
                limit=limit,
                total_items=total_count,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1
            )
            
            return ContentListResult(items=content_items, pagination=pagination)

    async def create_content(self, content_data: ContentCreateRequest) -> ContentItemModel:
        """Create new content item"""
        with db_manager.get_session() as session:
            content_repo = ContentRepository(session)
            tag_repo = ContentTagRepository(session)
            
            # Create content item
            db_content_data = {
                "name": content_data.name,
                "content_type": content_data.content_type.value,
                "status": ContentStatus.NEW.value,
                "priority": content_data.priority.value,
                "description": content_data.description,
                "meta_data": content_data.metadata,
                "created_by": "admin-001"  # Should come from current user context
            }
            
            db_content = content_repo.create(db_content_data)
            
            # Add tags if provided
            if content_data.tags:
                tag_repo.add_tags(db_content.id, content_data.tags)
            
            content_repo.commit()
            
            logger.info(f"Created new content: {db_content.name} ({db_content.id})")
            
            # Return as Pydantic model
            return self._convert_db_content_to_model(db_content)

    async def get_content_by_id(self, content_id: str) -> Optional[ContentItemModel]:
        """Get content item by ID"""
        with db_manager.get_session() as session:
            content_repo = ContentRepository(session)
            db_content = content_repo.get_by_id(content_id)
            
            if db_content:
                return self._convert_db_content_to_model(db_content)
            return None

    async def update_content(
        self, 
        content_id: str, 
        content_data: ContentUpdateRequest
    ) -> Optional[ContentItemModel]:
        """Update content item"""
        with db_manager.get_session() as session:
            content_repo = ContentRepository(session)
            tag_repo = ContentTagRepository(session)
            
            # Convert Pydantic model to dict and filter out None values
            update_data = {k: v.value if hasattr(v, 'value') else v 
                          for k, v in content_data.dict(exclude_unset=True).items() 
                          if v is not None}
            
            # Handle tags separately
            tags = update_data.pop('tags', None)
            
            db_content = content_repo.update(content_id, update_data)
            if not db_content:
                return None
            
            # Update tags if provided
            if tags is not None:
                tag_repo.add_tags(content_id, tags)
            
            content_repo.commit()
            
            logger.info(f"Updated content: {db_content.name} ({content_id})")
            return self._convert_db_content_to_model(db_content)

    async def update_status(self, content_id: str, status: ContentStatus) -> bool:
        """Update content status"""
        with db_manager.get_session() as session:
            content_repo = ContentRepository(session)
            
            result = content_repo.update_status(content_id, status)
            if result:
                content_repo.commit()
                logger.info(f"Updated content status: {content_id} to {status.value}")
            
            return result

    async def delete_content(self, content_id: str) -> bool:
        """Delete content item"""
        with db_manager.get_session() as session:
            content_repo = ContentRepository(session)
            
            result = content_repo.delete(content_id)
            if result:
                content_repo.commit()
                logger.info(f"Deleted content: {content_id}")
            
            return result

    async def bulk_update(
        self, 
        content_ids: List[str], 
        updates: Dict[str, Any]
    ) -> BulkUpdateResult:
        """Bulk update multiple content items"""
        with db_manager.get_session() as session:
            content_repo = ContentRepository(session)
            
            # Convert enum values to strings if needed
            processed_updates = {}
            for key, value in updates.items():
                if hasattr(value, 'value'):  # Handle enum values
                    processed_updates[key] = value.value
                else:
                    processed_updates[key] = value
            
            result = content_repo.bulk_update(content_ids, processed_updates)
            content_repo.commit()
            
            logger.info(f"Bulk update completed: {result['updated_count']} updated, {result['failed_count']} failed")
            
            return BulkUpdateResult(
                updated_count=result['updated_count'],
                failed_count=result['failed_count'],
                errors=result['errors']
            )

    async def get_movies_list(
        self, 
        page: int, 
        limit: int, 
        filters: MovieFilters
    ) -> MoviesListResult:
        """Get paginated movies list with filtering"""
        with db_manager.get_session() as session:
            movie_repo = MovieRepository(session)
            db_movies_list, total_count = movie_repo.get_list(page, limit, filters)
            
            # Convert to Pydantic models
            movies = [self._convert_db_movie_to_model(db_movie) for db_movie in db_movies_list]
            
            # Calculate pagination
            total_pages = (total_count + limit - 1) // limit
            
            pagination = PaginationInfo(
                page=page,
                limit=limit,
                total_items=total_count,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1
            )
            
            return MoviesListResult(items=movies, pagination=pagination)

    async def create_movie(self, movie_data) -> MovieModel:
        """Create new movie"""
        with db_manager.get_session() as session:
            movie_repo = MovieRepository(session)
            cast_repo = MovieCastRepository(session)
            
            # Create movie data
            db_movie_data = {
                "title": movie_data.title,
                "genre": movie_data.genre,
                "release_date": movie_data.release_date,
                "duration_minutes": movie_data.duration_minutes,
                "description": movie_data.description,
                "director": movie_data.director,
                "rating": movie_data.rating,
                "language": movie_data.language,
                "country": movie_data.country,
                "status": movie_data.status.value if movie_data.status else ContentStatus.NEW.value,
                "created_by": "admin-001"  # Should come from current user context
            }
            
            db_movie = movie_repo.create(db_movie_data)
            
            # Add cast members if provided
            if movie_data.cast:
                cast_data = [{"actor_name": actor, "role_type": "lead", "order_index": i} 
                           for i, actor in enumerate(movie_data.cast)]
                cast_repo.add_cast_members(db_movie.id, cast_data)
            
            movie_repo.commit()
            
            logger.info(f"Created new movie: {db_movie.title} ({db_movie.id})")
            
            return self._convert_db_movie_to_model(db_movie)
    
    async def update_movie(self, movie_id: str, movie_data) -> Optional[MovieModel]:
        """Update existing movie"""
        with db_manager.get_session() as session:
            movie_repo = MovieRepository(session)
            cast_repo = MovieCastRepository(session)
            
            # Convert Pydantic model to dict and filter out None values
            update_data = {k: v.value if hasattr(v, 'value') else v 
                          for k, v in movie_data.dict(exclude_unset=True).items() 
                          if v is not None}
            
            # Handle cast separately
            cast = update_data.pop('cast', None)
            
            db_movie = movie_repo.update(movie_id, update_data)
            if not db_movie:
                return None
            
            # Update cast if provided
            if cast is not None:
                cast_data = [{"actor_name": actor, "role_type": "lead", "order_index": i} 
                           for i, actor in enumerate(cast)]
                cast_repo.add_cast_members(movie_id, cast_data)
            
            movie_repo.commit()
            
            logger.info(f"Updated movie: {db_movie.title} ({movie_id})")
            return self._convert_db_movie_to_model(db_movie)
    
    async def delete_movie(self, movie_id: str) -> bool:
        """Delete movie"""
        with db_manager.get_session() as session:
            movie_repo = MovieRepository(session)
            
            result = movie_repo.delete(movie_id)
            if result:
                movie_repo.commit()
                logger.info(f"Deleted movie: {movie_id}")
            
            return result
    
    async def get_movie_by_id(self, movie_id: str) -> Optional[MovieModel]:
        """Get movie by ID"""
        with db_manager.get_session() as session:
            movie_repo = MovieRepository(session)
            db_movie = movie_repo.get_by_id(movie_id)
            
            if db_movie:
                return self._convert_db_movie_to_model(db_movie)
            return None

    async def start_export(
        self, 
        format: str, 
        content_type: Optional[str], 
        status: Optional[str]
    ) -> str:
        """Start data export process"""
        export_id = str(uuid.uuid4())
        logger.info(f"Started export {export_id} in format {format}")
        
        # Store export parameters for the background task
        if not hasattr(self, 'export_requests'):
            self.export_requests = {}
        
        self.export_requests[export_id] = {
            "format": format,
            "content_type": content_type,
            "status": status,
            "created_at": datetime.now().isoformat()
        }
        
        return export_id

    async def generate_export(self, export_id: str):
        """Generate export file (background task)"""
        try:
            import os
            import json
            import pandas as pd
            from pathlib import Path
            
            # Get export parameters
            if not hasattr(self, 'export_requests') or export_id not in self.export_requests:
                logger.error(f"Export request {export_id} not found")
                return
            
            export_request = self.export_requests[export_id]
            format = export_request["format"]
            
            # Create exports directory if it doesn't exist
            exports_dir = Path("exports")
            exports_dir.mkdir(exist_ok=True)
            
            # Get movies data from database
            movies_data = []
            with db_manager.get_session() as session:
                movies = session.query(Movie).all()
                
                for movie in movies:
                    movie_dict = {
                        "id": movie.id,
                        "title": movie.title,
                        "genre": movie.genre,
                        "director": movie.director,
                        "language": movie.language,
                        "duration_minutes": movie.duration_minutes,
                        "status": movie.status,
                        "release_date": movie.release_date.strftime("%Y-%m-%d") if movie.release_date else None,
                        "description": movie.description,
                        "rating": movie.rating,
                        "country": movie.country,
                        "poster_url": movie.poster_url,
                        "trailer_url": movie.trailer_url,
                        "imdb_id": movie.imdb_id,
                        "tmdb_id": movie.tmdb_id,
                        "box_office_collection": movie.box_office_collection,
                        "budget": movie.budget,
                        "is_available": movie.is_available,
                        "location": movie.location,
                        "created_at": movie.created_at.strftime("%Y-%m-%d %H:%M:%S") if movie.created_at else None,
                        "updated_at": movie.updated_at.strftime("%Y-%m-%d %H:%M:%S") if movie.updated_at else None
                    }
                    movies_data.append(movie_dict)
            
            # Export to different formats
            export_file_path = None
            format_ext = str(format).lower()
            
            if format_ext == "csv":
                export_file_path = exports_dir / f"{export_id}.csv"
                df = pd.DataFrame(movies_data)
                df.to_csv(export_file_path, index=False)
                
            elif format_ext == "json":
                export_file_path = exports_dir / f"{export_id}.json"
                with open(export_file_path, 'w', encoding='utf-8') as f:
                    json.dump(movies_data, f, indent=2, ensure_ascii=False)
                    
            elif format_ext == "xlsx":
                export_file_path = exports_dir / f"{export_id}.xlsx"
                df = pd.DataFrame(movies_data)
                df.to_excel(export_file_path, index=False, engine='openpyxl')
            
            # Store export info in a simple registry (could be database in production)
            if not hasattr(self, 'export_registry'):
                self.export_registry = {}
            
            self.export_registry[export_id] = {
                "file_path": str(export_file_path),
                "format": format_ext,
                "created_at": pd.Timestamp.now().isoformat(),
                "status": "completed"
            }
            
            logger.info(f"Export {export_id} completed successfully: {export_file_path}")
            
        except Exception as e:
            logger.error(f"Export {export_id} failed: {str(e)}")
            if hasattr(self, 'export_registry'):
                self.export_registry[export_id] = {
                    "status": "failed",
                    "error": str(e),
                    "created_at": pd.Timestamp.now().isoformat()
                }
    
    def get_export_file_path(self, export_id: str) -> Optional[str]:
        """Get export file path by export ID"""
        if hasattr(self, 'export_registry') and export_id in self.export_registry:
            export_info = self.export_registry[export_id]
            if export_info.get("status") == "completed":
                return export_info.get("file_path")
        return None

    async def bulk_import_movies(self, movies_data: List[Dict], operation: str = "upsert") -> Dict:
        """Bulk import/update movies from data list"""
        import_id = str(uuid.uuid4())
        logger.info(f"Starting bulk movie import {import_id} with {len(movies_data)} movies, operation: {operation}")
        
        result = {
            "import_id": import_id,
            "total_processed": len(movies_data),
            "successful": 0,
            "failed": 0,
            "created": 0,
            "updated": 0,
            "errors": [],
            "warnings": []
        }
        
        try:
            with db_manager.get_session() as session:
                for i, movie_data in enumerate(movies_data):
                    try:
                        # Clean and validate movie data
                        cleaned_data = self._clean_movie_data(movie_data)
                        
                        # Check if movie exists by title (for update/upsert operations)
                        existing_movie = None
                        if operation in ["update", "upsert"]:
                            existing_movie = session.query(Movie).filter(
                                Movie.title == cleaned_data.get("title")
                            ).first()
                        
                        if operation == "create":
                            # Create new movie only
                            if existing_movie:
                                result["errors"].append({
                                    "row": i + 1,
                                    "title": cleaned_data.get("title", "Unknown"),
                                    "error": "Movie already exists"
                                })
                                result["failed"] += 1
                                continue
                            
                            new_movie = Movie(**cleaned_data)
                            session.add(new_movie)
                            result["created"] += 1
                            result["successful"] += 1
                            
                        elif operation == "update":
                            # Update existing movie only
                            if not existing_movie:
                                result["errors"].append({
                                    "row": i + 1,
                                    "title": cleaned_data.get("title", "Unknown"),
                                    "error": "Movie not found for update"
                                })
                                result["failed"] += 1
                                continue
                            
                            for key, value in cleaned_data.items():
                                if hasattr(existing_movie, key) and value is not None:
                                    setattr(existing_movie, key, value)
                            
                            existing_movie.updated_at = datetime.now()
                            result["updated"] += 1
                            result["successful"] += 1
                            
                        elif operation == "upsert":
                            # Create or update
                            if existing_movie:
                                # Update existing
                                for key, value in cleaned_data.items():
                                    if hasattr(existing_movie, key) and value is not None:
                                        setattr(existing_movie, key, value)
                                existing_movie.updated_at = datetime.now()
                                result["updated"] += 1
                            else:
                                # Create new
                                new_movie = Movie(**cleaned_data)
                                session.add(new_movie)
                                result["created"] += 1
                            
                            result["successful"] += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing movie row {i + 1}: {str(e)}")
                        result["errors"].append({
                            "row": i + 1,
                            "title": movie_data.get("title", "Unknown"),
                            "error": str(e)
                        })
                        result["failed"] += 1
                
                # Commit all changes
                session.commit()
                logger.info(f"Bulk import {import_id} completed: {result['successful']} successful, {result['failed']} failed")
                
        except Exception as e:
            logger.error(f"Critical error in bulk import {import_id}: {str(e)}")
            result["errors"].append({
                "row": "all",
                "title": "System Error",
                "error": f"Critical import error: {str(e)}"
            })
            result["failed"] = result["total_processed"]
            result["successful"] = 0
        
        return result

    def _clean_movie_data(self, raw_data: Dict) -> Dict:
        """Clean and validate movie data for database insertion"""
        from datetime import datetime
        
        cleaned = {}
        
        # Required fields
        cleaned["title"] = str(raw_data.get("title", "")).strip()
        if not cleaned["title"]:
            raise ValueError("Title is required")
        
        cleaned["genre"] = str(raw_data.get("genre", "")).strip()
        if not cleaned["genre"]:
            raise ValueError("Genre is required")
        
        # Optional fields with proper type conversion
        if raw_data.get("release_date"):
            try:
                if isinstance(raw_data["release_date"], str):
                    cleaned["release_date"] = datetime.strptime(raw_data["release_date"], "%Y-%m-%d")
                else:
                    cleaned["release_date"] = raw_data["release_date"]
            except (ValueError, TypeError):
                pass  # Skip invalid dates
        
        if raw_data.get("duration_minutes"):
            try:
                cleaned["duration_minutes"] = int(raw_data["duration_minutes"])
            except (ValueError, TypeError):
                pass
        
        # String fields
        string_fields = ["description", "director", "rating", "language", "country", 
                        "poster_url", "trailer_url", "imdb_id", "tmdb_id"]
        for field in string_fields:
            if raw_data.get(field):
                cleaned[field] = str(raw_data[field]).strip()
        
        # Financial fields
        for field in ["box_office_collection", "budget"]:
            if raw_data.get(field):
                try:
                    cleaned[field] = float(raw_data[field])
                except (ValueError, TypeError):
                    pass
        
        # Status field validation
        valid_statuses = ["Ready", "Uploaded", "In Progress", "New", "Failed", "Processing"]
        if raw_data.get("status"):
            status = str(raw_data["status"]).strip()
            if status in valid_statuses:
                cleaned["status"] = status
            else:
                cleaned["status"] = "New"  # Default status
        else:
            cleaned["status"] = "New"
        
        # Boolean field: is_available
        if raw_data.get("is_available") is not None:
            if isinstance(raw_data["is_available"], bool):
                cleaned["is_available"] = raw_data["is_available"]
            else:
                # Convert string to boolean
                str_val = str(raw_data["is_available"]).lower().strip()
                cleaned["is_available"] = str_val in ["true", "1", "yes", "y", "available"]
        else:
            cleaned["is_available"] = True  # Default to available
        
        # Location field
        if raw_data.get("location"):
            cleaned["location"] = str(raw_data["location"]).strip()
        
        # Set timestamps
        cleaned["created_at"] = datetime.now()
        cleaned["updated_at"] = datetime.now()
        
        return cleaned

    async def parse_uploaded_file(self, file_content: bytes, file_type: str) -> List[Dict]:
        """Parse uploaded file content and return list of movie data"""
        import pandas as pd
        import json
        from io import BytesIO, StringIO
        
        try:
            if file_type.lower() == "csv":
                # Parse CSV
                content_str = file_content.decode('utf-8')
                df = pd.read_csv(StringIO(content_str))
                return df.to_dict('records')
                
            elif file_type.lower() in ["xlsx", "excel"]:
                # Parse Excel
                df = pd.read_excel(BytesIO(file_content), sheet_name=0)
                return df.to_dict('records')
                
            elif file_type.lower() == "json":
                # Parse JSON
                content_str = file_content.decode('utf-8')
                data = json.loads(content_str)
                
                # Handle different JSON structures
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "movies" in data:
                    return data["movies"]
                else:
                    raise ValueError("Invalid JSON structure. Expected list of movies or object with 'movies' key.")
                    
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
                
        except Exception as e:
            logger.error(f"Error parsing file: {str(e)}")
            raise ValueError(f"Failed to parse {file_type} file: {str(e)}")

    async def refresh_cache(self):
        """Refresh cached data"""
        logger.info("Refreshing content cache")
        self.cache.clear()

    # Note: Filtering is now handled in the database repository layer
    # These methods are no longer needed as filtering is done via SQL queries