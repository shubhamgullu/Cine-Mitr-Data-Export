"""
Database repository layer for CineMitr
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func, text
from datetime import datetime, timedelta
import uuid
import json

from database.models import (
    User, Movie, MovieCast, ContentItem, ContentTag, 
    Upload, ExportJob, AnalyticsMetric, SystemConfig, AuditLog
)
from models import (
    ContentFilters, MovieFilters, ContentStatus, Priority, 
    ContentType, PaginationInfo, UploadStatus
)

class BaseRepository:
    def __init__(self, session: Session):
        self.session = session

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

class UserRepository(BaseRepository):
    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.session.query(User).filter(User.id == user_id).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        return self.session.query(User).filter(User.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter(User.email == email).first()
    
    def create(self, user_data: Dict[str, Any]) -> User:
        user = User(**user_data)
        self.session.add(user)
        self.session.flush()
        return user

class MovieRepository(BaseRepository):
    def get_by_id(self, movie_id: str) -> Optional[Movie]:
        return self.session.query(Movie).options(
            joinedload(Movie.cast_members),
            joinedload(Movie.content_items)
        ).filter(Movie.id == movie_id).first()
    
    def get_list(self, page: int, limit: int, filters: MovieFilters) -> Tuple[List[Movie], int]:
        query = self.session.query(Movie)
        
        # Apply filters
        if filters.genre:
            query = query.filter(Movie.genre.ilike(f"%{filters.genre}%"))
        
        if filters.status:
            query = query.filter(Movie.status == filters.status)
        
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(or_(
                Movie.title.ilike(search_term),
                Movie.description.ilike(search_term),
                Movie.director.ilike(search_term)
            ))
        
        if filters.release_year:
            query = query.filter(func.year(Movie.release_date) == filters.release_year)
        
        if filters.language:
            query = query.filter(Movie.language.ilike(f"%{filters.language}%"))
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and ordering
        movies = query.order_by(desc(Movie.updated_at)).offset((page - 1) * limit).limit(limit).all()
        
        return movies, total_count
    
    def create(self, movie_data: Dict[str, Any]) -> Movie:
        movie = Movie(**movie_data)
        self.session.add(movie)
        self.session.flush()
        return movie
    
    def update(self, movie_id: str, movie_data: Dict[str, Any]) -> Optional[Movie]:
        movie = self.get_by_id(movie_id)
        if not movie:
            return None
        
        for key, value in movie_data.items():
            if hasattr(movie, key):
                setattr(movie, key, value)
        
        movie.updated_at = datetime.utcnow()
        self.session.flush()
        return movie
    
    def delete(self, movie_id: str) -> bool:
        movie = self.get_by_id(movie_id)
        if not movie:
            return False
        
        self.session.delete(movie)
        self.session.flush()
        return True

class ContentRepository(BaseRepository):
    def get_by_id(self, content_id: str) -> Optional[ContentItem]:
        """Get content item by ID with schema-safe querying"""
        try:
            from database.schema_utils import check_content_schema_migration
            
            if check_content_schema_migration(self.session):
                # Use full ORM query with new columns
                return self.session.query(ContentItem).options(
                    joinedload(ContentItem.movie),
                    joinedload(ContentItem.tags),
                    joinedload(ContentItem.creator)
                ).filter(ContentItem.id == content_id).first()
            else:
                # Use basic query without joins that might cause issues
                return self.session.query(ContentItem).filter(ContentItem.id == content_id).first()
                
        except Exception as e:
            # Fallback to simplest query
            try:
                return self.session.query(ContentItem).filter(ContentItem.id == content_id).first()
            except:
                return None
    
    def get_list(self, page: int, limit: int, filters: ContentFilters) -> Tuple[List[ContentItem], int]:
        """Get content items list with schema-safe querying"""
        try:
            from database.schema_utils import check_content_schema_migration
            
            # Check if new schema is available
            if check_content_schema_migration(self.session):
                # Use full ORM query with new columns
                query = self.session.query(ContentItem)
                
                # Apply filters
                if filters.status:
                    query = query.filter(ContentItem.status == filters.status)
                
                if filters.content_type:
                    query = query.filter(ContentItem.content_type == filters.content_type)
                
                if filters.priority:
                    query = query.filter(ContentItem.priority == filters.priority)
                
                if filters.search:
                    search_term = f"%{filters.search}%"
                    query = query.filter(or_(
                        ContentItem.name.ilike(search_term),
                        ContentItem.description.ilike(search_term)
                    ))
                
                if filters.created_after:
                    query = query.filter(ContentItem.created_at >= filters.created_after)
                
                if filters.created_before:
                    query = query.filter(ContentItem.created_at <= filters.created_before)
                
                # Get total count
                total_count = query.count()
                
                # Apply pagination and ordering
                content_items = query.options(
                    joinedload(ContentItem.movie),
                    joinedload(ContentItem.tags)
                ).order_by(desc(ContentItem.updated_at)).offset((page - 1) * limit).limit(limit).all()
                
                return content_items, total_count
            else:
                # Use basic SQL query for compatibility
                return self._get_list_basic_schema(page, limit, filters)
                
        except Exception as e:
            # Fallback to basic schema
            return self._get_list_basic_schema(page, limit, filters)
    
    def _get_list_basic_schema(self, page: int, limit: int, filters: ContentFilters) -> Tuple[List[ContentItem], int]:
        """Fallback method for basic schema without new columns"""
        from sqlalchemy import text
        
        # Build WHERE clause
        where_conditions = []
        params = {"limit": limit, "offset": (page - 1) * limit}
        
        if filters.status:
            where_conditions.append("status = :status")
            params["status"] = filters.status
        
        if filters.content_type:
            where_conditions.append("content_type = :content_type")
            params["content_type"] = filters.content_type
        
        if filters.priority:
            where_conditions.append("priority = :priority")
            params["priority"] = filters.priority
        
        if filters.search:
            where_conditions.append("(name LIKE :search OR description LIKE :search)")
            params["search"] = f"%{filters.search}%"
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Count query
        count_result = self.session.execute(text(f"""
            SELECT COUNT(*) FROM content_items WHERE {where_clause}
        """), params)
        total_count = count_result.scalar()
        
        # Main query
        result = self.session.execute(text(f"""
            SELECT 
                id, name, content_type, status, priority, description,
                file_path, file_size_bytes, duration_seconds, thumbnail_url,
                metadata, movie_id, created_at, updated_at
            FROM content_items 
            WHERE {where_clause}
            ORDER BY updated_at DESC 
            LIMIT :limit OFFSET :offset
        """), params)
        
        # Convert results to ContentItem-like objects
        content_items = []
        for row in result.fetchall():
            item = type('ContentItem', (), {})()
            item.id = row[0]
            item.name = row[1]
            item.content_type = row[2]
            item.status = row[3]
            item.priority = row[4]
            item.description = row[5]
            item.file_path = row[6]
            item.file_size_bytes = row[7]
            item.duration_seconds = row[8]
            item.thumbnail_url = row[9]
            item.meta_data = row[10]
            item.movie_id = row[11]
            item.created_at = row[12]
            item.updated_at = row[13]
            # Set default values for new fields
            item.link_url = None
            item.movie_name = None
            item.local_status = 'Pending'
            item.edited_status = 'Pending'
            item.content_to_add = None
            item.source_folder = None
            content_items.append(item)
        
        return content_items, total_count
    
    def create(self, content_data: Dict[str, Any]) -> ContentItem:
        """Create content item with schema-safe field handling"""
        try:
            from database.schema_utils import check_content_schema_migration
            
            # Filter content data based on available schema
            if not check_content_schema_migration(self.session):
                # Remove new fields if schema hasn't been migrated
                safe_data = content_data.copy()
                new_fields = ['link_url', 'movie_name', 'local_status', 'edited_status', 'content_to_add', 'source_folder']
                for field in new_fields:
                    safe_data.pop(field, None)
                content_data = safe_data
            
            content = ContentItem(**content_data)
            self.session.add(content)
            self.session.flush()
            return content
            
        except Exception as e:
            # Fallback: try with basic fields only
            basic_fields = {
                'name': content_data.get('name'),
                'content_type': content_data.get('content_type'),
                'status': content_data.get('status', 'New'),
                'priority': content_data.get('priority', 'Medium'),
                'description': content_data.get('description'),
                'file_path': content_data.get('file_path'),
                'file_size_bytes': content_data.get('file_size_bytes'),
                'duration_seconds': content_data.get('duration_seconds'),
                'metadata': content_data.get('metadata')
            }
            # Remove None values
            basic_fields = {k: v for k, v in basic_fields.items() if v is not None}
            
            content = ContentItem(**basic_fields)
            self.session.add(content)
            self.session.flush()
            return content
    
    def update(self, content_id: str, content_data: Dict[str, Any]) -> Optional[ContentItem]:
        """Update content item with schema-safe field handling"""
        content = self.get_by_id(content_id)
        if not content:
            return None
        
        try:
            from database.schema_utils import check_content_schema_migration
            
            # Filter content data based on available schema
            if not check_content_schema_migration(self.session):
                # Remove new fields if schema hasn't been migrated
                safe_data = content_data.copy()
                new_fields = ['link_url', 'movie_name', 'local_status', 'edited_status', 'content_to_add', 'source_folder']
                for field in new_fields:
                    safe_data.pop(field, None)
                content_data = safe_data
            
            for key, value in content_data.items():
                if hasattr(content, key):
                    setattr(content, key, value)
            
            content.updated_at = datetime.utcnow()
            self.session.flush()
            return content
            
        except Exception as e:
            # Fallback: update only basic fields
            basic_fields = ['name', 'content_type', 'status', 'priority', 'description', 
                          'file_path', 'file_size_bytes', 'duration_seconds', 'metadata']
            
            for key, value in content_data.items():
                if key in basic_fields and hasattr(content, key):
                    setattr(content, key, value)
            
            content.updated_at = datetime.utcnow()
            self.session.flush()
            return content
    
    def update_status(self, content_id: str, status: ContentStatus) -> bool:
        content = self.get_by_id(content_id)
        if not content:
            return False
        
        content.status = status.value
        content.updated_at = datetime.utcnow()
        self.session.flush()
        return True
    
    def delete(self, content_id: str) -> bool:
        content = self.get_by_id(content_id)
        if not content:
            return False
        
        self.session.delete(content)
        self.session.flush()
        return True
    
    def bulk_update(self, content_ids: List[str], updates: Dict[str, Any]) -> Dict[str, Any]:
        updated_count = 0
        failed_count = 0
        errors = []
        
        for content_id in content_ids:
            try:
                content = self.get_by_id(content_id)
                if not content:
                    failed_count += 1
                    errors.append({"content_id": content_id, "error": "Content not found"})
                    continue
                
                for key, value in updates.items():
                    if hasattr(content, key):
                        setattr(content, key, value)
                
                content.updated_at = datetime.utcnow()
                updated_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append({"content_id": content_id, "error": str(e)})
        
        self.session.flush()
        
        return {
            "updated_count": updated_count,
            "failed_count": failed_count,
            "errors": errors
        }
    
    def get_recent_activity(self, limit: int = 10) -> List[ContentItem]:
        """Get recent activity with schema-safe querying"""
        try:
            from database.schema_utils import check_content_schema_migration
            
            # Check if new schema is available
            if check_content_schema_migration(self.session):
                # Use full query with new columns
                return self.session.query(ContentItem).options(
                    joinedload(ContentItem.movie)
                ).order_by(desc(ContentItem.updated_at)).limit(limit).all()
            else:
                # Use basic query without new columns
                from sqlalchemy import text
                result = self.session.execute(text("""
                    SELECT 
                        id, name, content_type, status, priority, description,
                        file_path, file_size_bytes, duration_seconds, thumbnail_url,
                        metadata, movie_id, created_at, updated_at
                    FROM content_items 
                    ORDER BY updated_at DESC 
                    LIMIT :limit
                """), {"limit": limit})
                
                # Convert results to ContentItem-like objects
                content_items = []
                for row in result.fetchall():
                    # Create a minimal ContentItem object
                    item = type('ContentItem', (), {})()
                    item.id = row[0]
                    item.name = row[1]
                    item.content_type = row[2]
                    item.status = row[3]
                    item.priority = row[4]
                    item.description = row[5]
                    item.file_path = row[6]
                    item.file_size_bytes = row[7]
                    item.duration_seconds = row[8]
                    item.thumbnail_url = row[9]
                    item.meta_data = row[10]
                    item.movie_id = row[11]
                    item.created_at = row[12]
                    item.updated_at = row[13]
                    # Set default values for new fields
                    item.link_url = None
                    item.movie_name = None
                    item.local_status = 'Pending'
                    item.edited_status = 'Pending'
                    item.content_to_add = None
                    item.source_folder = None
                    content_items.append(item)
                
                return content_items
                
        except Exception as e:
            # Fallback to basic query if schema check fails
            try:
                return self.session.query(ContentItem).order_by(desc(ContentItem.updated_at)).limit(limit).all()
            except:
                # Last resort: return empty list
                return []

class ContentTagRepository(BaseRepository):
    def add_tags(self, content_id: str, tags: List[str]):
        # Remove existing tags for this content
        self.session.query(ContentTag).filter(ContentTag.content_id == content_id).delete()
        
        # Add new tags
        for tag_name in tags:
            tag = ContentTag(content_id=content_id, tag_name=tag_name)
            self.session.add(tag)
        
        self.session.flush()
    
    def get_by_content_id(self, content_id: str) -> List[ContentTag]:
        return self.session.query(ContentTag).filter(ContentTag.content_id == content_id).all()

class MovieCastRepository(BaseRepository):
    def add_cast_members(self, movie_id: str, cast_data: List[Dict[str, Any]]):
        # Remove existing cast for this movie
        self.session.query(MovieCast).filter(MovieCast.movie_id == movie_id).delete()
        
        # Add new cast members
        for cast_member in cast_data:
            cast = MovieCast(movie_id=movie_id, **cast_member)
            self.session.add(cast)
        
        self.session.flush()
    
    def get_by_movie_id(self, movie_id: str) -> List[MovieCast]:
        return self.session.query(MovieCast).filter(MovieCast.movie_id == movie_id).order_by(MovieCast.order_index).all()

class UploadRepository(BaseRepository):
    def get_by_id(self, upload_id: str) -> Optional[Upload]:
        return self.session.query(Upload).filter(Upload.upload_id == upload_id).first()
    
    def create(self, upload_data: Dict[str, Any]) -> Upload:
        upload = Upload(**upload_data)
        self.session.add(upload)
        self.session.flush()
        return upload
    
    def update_status(self, upload_id: str, status: UploadStatus, **kwargs) -> bool:
        upload = self.get_by_id(upload_id)
        if not upload:
            return False
        
        upload.status = status.value
        upload.updated_at = datetime.utcnow()
        
        for key, value in kwargs.items():
            if hasattr(upload, key):
                setattr(upload, key, value)
        
        self.session.flush()
        return True

class AnalyticsRepository(BaseRepository):
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        # Get basic counts
        total_movies = self.session.query(Movie).count()
        total_content = self.session.query(ContentItem).count()
        uploaded_content = self.session.query(ContentItem).filter(ContentItem.status == 'Uploaded').count()
        pending_content = self.session.query(ContentItem).filter(ContentItem.status.in_(['New', 'In Progress'])).count()
        
        # Calculate storage used
        storage_query = self.session.query(func.sum(ContentItem.file_size_bytes)).filter(ContentItem.file_size_bytes.isnot(None)).scalar()
        storage_used_gb = round((storage_query or 0) / (1024 ** 3), 2)
        
        # Calculate upload rate
        upload_rate = round((uploaded_content / max(total_content, 1)) * 100, 2)
        
        # Weekly change (mock for now)
        uploaded_weekly_change = 5  # This should be calculated based on actual data
        
        return {
            "total_movies": total_movies,
            "content_items": total_content,
            "uploaded": uploaded_content,
            "uploaded_weekly_change": uploaded_weekly_change,
            "pending": pending_content,
            "upload_rate": upload_rate,
            "storage_used_gb": storage_used_gb,
            "storage_total_gb": 1000.0,  # This should come from config
            "active_uploads": 0,  # This should be calculated from active uploads
            "failed_uploads": 0   # This should be calculated from failed uploads
        }
    
    def get_status_distribution(self) -> Dict[str, int]:
        result = self.session.query(
            ContentItem.status,
            func.count(ContentItem.id)
        ).group_by(ContentItem.status).all()
        
        distribution = {
            "ready": 0,
            "uploaded": 0,
            "in_progress": 0,
            "new": 0,
            "failed": 0,
            "processing": 0
        }
        
        for status, count in result:
            key = status.lower().replace(" ", "_")
            if key in distribution:
                distribution[key] = count
        
        return distribution
    
    def get_priority_distribution(self) -> Dict[str, int]:
        result = self.session.query(
            ContentItem.priority,
            func.count(ContentItem.id)
        ).group_by(ContentItem.priority).all()
        
        distribution = {"high": 0, "medium": 0, "low": 0}
        
        for priority, count in result:
            key = priority.lower()
            if key in distribution:
                distribution[key] = count
        
        return distribution
    
    def get_storage_stats(self) -> Dict[str, Any]:
        # Content by type with sizes
        content_stats = self.session.query(
            ContentItem.content_type,
            func.count(ContentItem.id).label('file_count'),
            func.sum(ContentItem.file_size_bytes).label('total_size'),
            func.avg(ContentItem.file_size_bytes).label('avg_size'),
            func.min(ContentItem.file_size_bytes).label('min_size'),
            func.max(ContentItem.file_size_bytes).label('max_size')
        ).filter(ContentItem.file_size_bytes.isnot(None)).group_by(ContentItem.content_type).all()
        
        total_size_bytes = sum(stat.total_size or 0 for stat in content_stats)
        total_size_gb = round(total_size_bytes / (1024 ** 3), 2)
        
        # Largest files
        largest_files = self.session.query(ContentItem).filter(
            ContentItem.file_size_bytes.isnot(None)
        ).order_by(desc(ContentItem.file_size_bytes)).limit(10).all()
        
        return {
            "total_size_gb": total_size_gb,
            "used_size_gb": total_size_gb,
            "available_size_gb": max(1000.0 - total_size_gb, 0),  # Config-based total
            "usage_percentage": round((total_size_gb / 1000.0) * 100, 2),
            "file_count": sum(stat.file_count for stat in content_stats),
            "largest_files": [
                {
                    "name": file.name,
                    "size_mb": round((file.file_size_bytes or 0) / (1024 ** 2), 2),
                    "type": file.content_type
                }
                for file in largest_files
            ]
        }

class SystemConfigRepository(BaseRepository):
    def get_by_key(self, key: str) -> Optional[SystemConfig]:
        return self.session.query(SystemConfig).filter(SystemConfig.config_key == key).first()
    
    def set_config(self, key: str, value: str, data_type: str = "string", description: str = None, updated_by: str = None):
        config = self.get_by_key(key)
        if config:
            config.config_value = value
            config.data_type = data_type
            config.description = description
            config.updated_by = updated_by
            config.updated_at = datetime.utcnow()
        else:
            config = SystemConfig(
                config_key=key,
                config_value=value,
                data_type=data_type,
                description=description,
                updated_by=updated_by
            )
            self.session.add(config)
        
        self.session.flush()
        return config

class AuditRepository(BaseRepository):
    def log_change(self, table_name: str, record_id: str, action: str, 
                   old_values: Dict = None, new_values: Dict = None, 
                   changed_by: str = None, change_reason: str = None):
        audit_log = AuditLog(
            table_name=table_name,
            record_id=record_id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            changed_by=changed_by,
            change_reason=change_reason
        )
        self.session.add(audit_log)
        self.session.flush()