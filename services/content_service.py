"""
Content management service for handling content-related operations
"""

import asyncio
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from models import (
    ContentItem, Movie, ContentCreateRequest, ContentUpdateRequest,
    ContentFilters, MovieFilters, ContentListResult, MoviesListResult,
    PaginationInfo, ContentStatus, Priority, ContentType, BulkUpdateResult
)
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ContentService:
    def __init__(self):
        self.content_storage = {}  # In-memory storage for demo
        self.movies_storage = {}   # In-memory storage for demo
        self.cache = {}
        self.cache_ttl = 300

    async def initialize(self):
        """Initialize the content service with sample data"""
        logger.info("Initializing Content Service")
        await self._populate_sample_data()

    async def _populate_sample_data(self):
        """Populate with sample content data"""
        sample_content = [
            {
                "id": "content_001",
                "name": "12th Fail",
                "content_type": ContentType.MOVIE,
                "status": ContentStatus.READY,
                "priority": Priority.HIGH,
                "description": "Inspirational drama about overcoming failures",
                "file_size_bytes": 2576588800,  # ~2.4GB
                "duration_seconds": 8820,  # 147 minutes
                "created_at": datetime.utcnow() - timedelta(days=2),
                "updated_at": datetime.utcnow() - timedelta(hours=2)
            },
            {
                "id": "content_002", 
                "name": "2 States",
                "content_type": ContentType.TRAILER,
                "status": ContentStatus.UPLOADED,
                "priority": Priority.MEDIUM,
                "description": "Romantic comedy trailer",
                "file_size_bytes": 163840000,  # ~156MB
                "duration_seconds": 180,  # 3 minutes
                "created_at": datetime.utcnow() - timedelta(days=5),
                "updated_at": datetime.utcnow() - timedelta(hours=4)
            },
            {
                "id": "content_003",
                "name": "Laal Singh Chaddha",
                "content_type": ContentType.MOVIE,
                "status": ContentStatus.IN_PROGRESS,
                "priority": Priority.MEDIUM,
                "description": "Adaptation of Forrest Gump",
                "file_size_bytes": 3402341376,  # ~3.2GB
                "duration_seconds": 9540,  # 159 minutes
                "created_at": datetime.utcnow() - timedelta(days=8),
                "updated_at": datetime.utcnow() - timedelta(hours=6)
            }
        ]

        for content_data in sample_content:
            content = ContentItem(
                **content_data,
                file_path=f"/content/{content_data['id']}.mp4",
                thumbnail_url=f"/thumbnails/{content_data['id']}.jpg",
                tags=["bollywood", "drama"],
                metadata={"resolution": "1080p", "codec": "h264"},
                created_by="admin"
            )
            self.content_storage[content.id] = content

        # Sample movies
        sample_movies = [
            {
                "id": "movie_001",
                "title": "12th Fail",
                "genre": "Drama",
                "release_date": datetime(2023, 10, 27),
                "duration_minutes": 147,
                "description": "Based on true events, about a man who overcomes extreme hardships",
                "director": "Vidhu Vinod Chopra",
                "cast": ["Vikrant Massey", "Medha Shankar"],
                "rating": "8.9",
                "language": "Hindi",
                "country": "India",
                "status": ContentStatus.READY,
                "created_at": datetime.utcnow() - timedelta(days=30),
                "updated_at": datetime.utcnow() - timedelta(days=1)
            },
            {
                "id": "movie_002",
                "title": "Pathaan",
                "genre": "Action",
                "release_date": datetime(2023, 1, 25),
                "duration_minutes": 146,
                "description": "An action thriller featuring a secret agent",
                "director": "Siddharth Anand",
                "cast": ["Shah Rukh Khan", "Deepika Padukone", "John Abraham"],
                "rating": "7.2",
                "language": "Hindi",
                "country": "India",
                "status": ContentStatus.UPLOADED,
                "created_at": datetime.utcnow() - timedelta(days=45),
                "updated_at": datetime.utcnow() - timedelta(days=2)
            }
        ]

        for movie_data in sample_movies:
            movie = Movie(**movie_data)
            self.movies_storage[movie.id] = movie

    async def get_content_list(
        self, 
        page: int, 
        limit: int, 
        filters: ContentFilters
    ) -> ContentListResult:
        """Get paginated content list with filtering"""
        await asyncio.sleep(0.1)  # Simulate database query
        
        all_content = list(self.content_storage.values())
        
        # Apply filters
        filtered_content = self._apply_content_filters(all_content, filters)
        
        # Sort by updated_at descending
        filtered_content.sort(key=lambda x: x.updated_at, reverse=True)
        
        # Calculate pagination
        total_items = len(filtered_content)
        total_pages = (total_items + limit - 1) // limit
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        items = filtered_content[start_idx:end_idx]
        
        pagination = PaginationInfo(
            page=page,
            limit=limit,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )
        
        return ContentListResult(items=items, pagination=pagination)

    async def create_content(self, content_data: ContentCreateRequest) -> ContentItem:
        """Create new content item"""
        await asyncio.sleep(0.1)
        
        content_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        content = ContentItem(
            id=content_id,
            name=content_data.name,
            content_type=content_data.content_type,
            status=ContentStatus.NEW,
            priority=content_data.priority,
            description=content_data.description,
            tags=content_data.tags or [],
            metadata=content_data.metadata or {},
            created_at=now,
            updated_at=now,
            created_by="current_user"
        )
        
        self.content_storage[content_id] = content
        logger.info(f"Created new content: {content.name} ({content_id})")
        
        return content

    async def get_content_by_id(self, content_id: str) -> Optional[ContentItem]:
        """Get content item by ID"""
        await asyncio.sleep(0.05)
        return self.content_storage.get(content_id)

    async def update_content(
        self, 
        content_id: str, 
        content_data: ContentUpdateRequest
    ) -> Optional[ContentItem]:
        """Update content item"""
        await asyncio.sleep(0.1)
        
        content = self.content_storage.get(content_id)
        if not content:
            return None
        
        # Update fields
        update_data = content_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(content, field, value)
        
        content.updated_at = datetime.utcnow()
        
        logger.info(f"Updated content: {content.name} ({content_id})")
        return content

    async def update_status(self, content_id: str, status: ContentStatus) -> bool:
        """Update content status"""
        await asyncio.sleep(0.05)
        
        content = self.content_storage.get(content_id)
        if not content:
            return False
        
        old_status = content.status
        content.status = status
        content.updated_at = datetime.utcnow()
        
        logger.info(f"Updated content status: {content.name} from {old_status} to {status}")
        return True

    async def delete_content(self, content_id: str) -> bool:
        """Delete content item"""
        await asyncio.sleep(0.05)
        
        if content_id in self.content_storage:
            content = self.content_storage[content_id]
            del self.content_storage[content_id]
            logger.info(f"Deleted content: {content.name} ({content_id})")
            return True
        
        return False

    async def bulk_update(
        self, 
        content_ids: List[str], 
        updates: Dict[str, Any]
    ) -> BulkUpdateResult:
        """Bulk update multiple content items"""
        await asyncio.sleep(0.2)
        
        updated_count = 0
        failed_count = 0
        errors = []
        
        for content_id in content_ids:
            try:
                content = self.content_storage.get(content_id)
                if not content:
                    failed_count += 1
                    errors.append({"content_id": content_id, "error": "Content not found"})
                    continue
                
                # Apply updates
                for field, value in updates.items():
                    if hasattr(content, field):
                        setattr(content, field, value)
                
                content.updated_at = datetime.utcnow()
                updated_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append({"content_id": content_id, "error": str(e)})
        
        logger.info(f"Bulk update completed: {updated_count} updated, {failed_count} failed")
        
        return BulkUpdateResult(
            updated_count=updated_count,
            failed_count=failed_count,
            errors=errors
        )

    async def get_movies_list(
        self, 
        page: int, 
        limit: int, 
        filters: MovieFilters
    ) -> MoviesListResult:
        """Get paginated movies list with filtering"""
        await asyncio.sleep(0.1)
        
        all_movies = list(self.movies_storage.values())
        
        # Apply filters
        filtered_movies = self._apply_movie_filters(all_movies, filters)
        
        # Sort by updated_at descending
        filtered_movies.sort(key=lambda x: x.updated_at, reverse=True)
        
        # Calculate pagination
        total_items = len(filtered_movies)
        total_pages = (total_items + limit - 1) // limit
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        items = filtered_movies[start_idx:end_idx]
        
        pagination = PaginationInfo(
            page=page,
            limit=limit,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )
        
        return MoviesListResult(items=items, pagination=pagination)

    async def create_movie(self, movie_data) -> Movie:
        """Create new movie"""
        await asyncio.sleep(0.1)
        
        movie_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        movie = Movie(
            id=movie_id,
            title=movie_data.title,
            genre=movie_data.genre,
            release_date=movie_data.release_date,
            duration_minutes=movie_data.duration_minutes,
            description=movie_data.description,
            director=movie_data.director,
            cast=movie_data.cast or [],
            rating=movie_data.rating,
            language=movie_data.language,
            country=movie_data.country,
            status=ContentStatus.NEW,
            created_at=now,
            updated_at=now
        )
        
        self.movies_storage[movie_id] = movie
        logger.info(f"Created new movie: {movie.title} ({movie_id})")
        
        return movie

    async def start_export(
        self, 
        format: str, 
        content_type: Optional[str], 
        status: Optional[str]
    ) -> str:
        """Start data export process"""
        export_id = str(uuid.uuid4())
        logger.info(f"Started export {export_id} in format {format}")
        return export_id

    async def generate_export(self, export_id: str):
        """Generate export file (background task)"""
        await asyncio.sleep(2)  # Simulate export generation
        logger.info(f"Export {export_id} completed")

    async def refresh_cache(self):
        """Refresh cached data"""
        logger.info("Refreshing content cache")
        self.cache.clear()

    def _apply_content_filters(
        self, 
        content_list: List[ContentItem], 
        filters: ContentFilters
    ) -> List[ContentItem]:
        """Apply filters to content list"""
        result = content_list.copy()
        
        if filters.status:
            result = [c for c in result if c.status.value == filters.status]
        
        if filters.content_type:
            result = [c for c in result if c.content_type.value == filters.content_type]
        
        if filters.priority:
            result = [c for c in result if c.priority.value == filters.priority]
        
        if filters.search:
            search_lower = filters.search.lower()
            result = [c for c in result if search_lower in c.name.lower()]
        
        if filters.created_after:
            result = [c for c in result if c.created_at >= filters.created_after]
        
        if filters.created_before:
            result = [c for c in result if c.created_at <= filters.created_before]
        
        return result

    def _apply_movie_filters(
        self, 
        movies_list: List[Movie], 
        filters: MovieFilters
    ) -> List[Movie]:
        """Apply filters to movies list"""
        result = movies_list.copy()
        
        if filters.genre:
            result = [m for m in result if m.genre.lower() == filters.genre.lower()]
        
        if filters.status:
            result = [m for m in result if m.status.value == filters.status]
        
        if filters.search:
            search_lower = filters.search.lower()
            result = [m for m in result if search_lower in m.title.lower()]
        
        if filters.release_year:
            result = [m for m in result 
                     if m.release_date and m.release_date.year == filters.release_year]
        
        if filters.language:
            result = [m for m in result 
                     if m.language and m.language.lower() == filters.language.lower()]
        
        return result