"""
SQLAlchemy database models for CineMitr
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, DECIMAL, Enum, ForeignKey, BigInteger, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(Enum('admin', 'editor', 'viewer', name='user_roles'), default='viewer', nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    created_movies = relationship("Movie", back_populates="creator", foreign_keys="Movie.created_by")
    created_content = relationship("ContentItem", back_populates="creator", foreign_keys="ContentItem.created_by")
    uploads = relationship("Upload", back_populates="uploader")
    sessions = relationship("UserSession", back_populates="user")

class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    genre = Column(String(100), nullable=False)
    release_date = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    director = Column(String(255), nullable=True)
    rating = Column(String(10), nullable=True)
    language = Column(String(50), nullable=True)
    country = Column(String(100), nullable=True)
    poster_url = Column(Text, nullable=True)
    trailer_url = Column(Text, nullable=True)
    status = Column(Enum('Ready', 'Uploaded', 'In Progress', 'New', 'Failed', 'Processing', name='content_status'), 
                   default='New', nullable=False)
    imdb_id = Column(String(20), nullable=True)
    tmdb_id = Column(String(20), nullable=True)
    box_office_collection = Column(DECIMAL(15, 2), nullable=True)
    budget = Column(DECIMAL(15, 2), nullable=True)
    created_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="created_movies", foreign_keys=[created_by])
    cast_members = relationship("MovieCast", back_populates="movie")
    content_items = relationship("ContentItem", back_populates="movie")

class MovieCast(Base):
    __tablename__ = "movie_cast"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    movie_id = Column(String(36), ForeignKey('movies.id'), nullable=False)
    actor_name = Column(String(255), nullable=False)
    character_name = Column(String(255), nullable=True)
    role_type = Column(Enum('lead', 'supporting', 'cameo', name='role_types'), default='supporting', nullable=False)
    order_index = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    movie = relationship("Movie", back_populates="cast_members")

class ContentItem(Base):
    __tablename__ = "content_items"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    content_type = Column(Enum('Movie', 'Reel', 'Trailer', 'Series', 'Documentary', name='content_types'), nullable=False)
    status = Column(Enum('Ready', 'Uploaded', 'In Progress', 'New', 'Failed', 'Processing', name='content_status'), 
                   default='New', nullable=False)
    priority = Column(Enum('High', 'Medium', 'Low', name='priority_levels'), default='Medium', nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(Text, nullable=True)
    file_size_bytes = Column(BigInteger, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    thumbnail_url = Column(Text, nullable=True)
    video_url = Column(Text, nullable=True)
    resolution = Column(String(20), nullable=True)
    codec = Column(String(50), nullable=True)
    bitrate = Column(Integer, nullable=True)
    frame_rate = Column(DECIMAL(5, 2), nullable=True)
    aspect_ratio = Column(String(20), nullable=True)
    quality = Column(Enum('SD', 'HD', '4K', '8K', name='quality_levels'), default='HD', nullable=True)
    meta_data = Column("metadata", JSON, nullable=True)
    movie_id = Column(String(36), ForeignKey('movies.id'), nullable=True)
    created_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    uploaded_at = Column(DateTime, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    movie = relationship("Movie", back_populates="content_items")
    creator = relationship("User", back_populates="created_content", foreign_keys=[created_by])
    tags = relationship("ContentTag", back_populates="content")
    uploads = relationship("Upload", back_populates="content_item")

class ContentTag(Base):
    __tablename__ = "content_tags"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content_id = Column(String(36), ForeignKey('content_items.id'), nullable=False)
    tag_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    content = relationship("ContentItem", back_populates="tags")

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")

class Upload(Base):
    __tablename__ = "uploads"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    upload_id = Column(String(36), unique=True, nullable=False)
    file_name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    content_type = Column(String(100), nullable=False)
    mime_type = Column(String(100), nullable=False)
    status = Column(Enum('pending', 'uploading', 'processing', 'completed', 'failed', name='upload_status'), 
                   default='pending', nullable=False)
    progress_percentage = Column(DECIMAL(5, 2), default=0.00, nullable=False)
    bytes_uploaded = Column(BigInteger, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    file_path = Column(Text, nullable=True)
    checksum = Column(String(64), nullable=True)
    content_item_id = Column(String(36), ForeignKey('content_items.id'), nullable=True)
    uploaded_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    content_item = relationship("ContentItem", back_populates="uploads")
    uploader = relationship("User", back_populates="uploads")

class ExportJob(Base):
    __tablename__ = "export_jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    export_id = Column(String(36), unique=True, nullable=False)
    format = Column(Enum('csv', 'json', 'xlsx', name='export_formats'), nullable=False)
    status = Column(Enum('pending', 'processing', 'completed', 'failed', name='export_status'), 
                   default='pending', nullable=False)
    filters = Column(JSON, nullable=True)
    file_path = Column(Text, nullable=True)
    file_size_bytes = Column(BigInteger, nullable=True)
    record_count = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    creator = relationship("User")

class AnalyticsMetric(Base):
    __tablename__ = "analytics_metrics"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(DECIMAL(15, 2), nullable=False)
    metric_type = Column(Enum('count', 'size', 'percentage', 'duration', 'rate', name='metric_types'), nullable=False)
    dimension = Column(String(100), nullable=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    meta_data = Column("metadata", JSON, nullable=True)
    recorded_at = Column(DateTime, default=func.now(), nullable=False)

class SystemConfig(Base):
    __tablename__ = "system_config"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text, nullable=False)
    data_type = Column(Enum('string', 'number', 'boolean', 'json', name='config_types'), default='string', nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    updated_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    updater = relationship("User")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    table_name = Column(String(100), nullable=False)
    record_id = Column(String(36), nullable=False)
    action = Column(Enum('INSERT', 'UPDATE', 'DELETE', name='audit_actions'), nullable=False)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    changed_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    change_reason = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")