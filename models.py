"""
Data models and Pydantic schemas for CineMitr API
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

# ============= ENUMS =============

class ContentStatus(str, Enum):
    READY = "Ready"
    UPLOADED = "Uploaded"
    IN_PROGRESS = "In Progress"
    NEW = "New"
    FAILED = "Failed"
    PROCESSING = "Processing"

class Priority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class ContentType(str, Enum):
    MOVIE = "Movie"
    REEL = "Reel"
    TRAILER = "Trailer"
    SERIES = "Series"
    DOCUMENTARY = "Documentary"

class UploadStatus(str, Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ExportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"
    XLSX = "xlsx"

# ============= BASE MODELS =============

class BaseResponse(BaseModel):
    success: bool
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    environment: str

class PaginationInfo(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool

# ============= DASHBOARD MODELS =============

class DashboardMetrics(BaseModel):
    total_movies: int = Field(..., description="Total number of movies")
    content_items: int = Field(..., description="Total content items")
    uploaded: int = Field(..., description="Number of uploaded items")
    uploaded_weekly_change: int = Field(..., description="Weekly change in uploads")
    pending: int = Field(..., description="Number of pending items")
    upload_rate: float = Field(..., description="Upload success rate percentage")
    storage_used_gb: float = Field(..., description="Storage used in GB")
    storage_total_gb: float = Field(..., description="Total storage in GB")
    active_uploads: int = Field(..., description="Number of active uploads")
    failed_uploads: int = Field(..., description="Number of failed uploads")

class StatusDistribution(BaseModel):
    ready: int
    uploaded: int
    in_progress: int
    new: int
    failed: Optional[int] = 0
    processing: Optional[int] = 0

class PriorityDistribution(BaseModel):
    high: int
    medium: int
    low: int

class StorageStats(BaseModel):
    total_size_gb: float
    used_size_gb: float
    available_size_gb: float
    usage_percentage: float
    file_count: int
    largest_files: List[Dict[str, Any]]

class RecentActivity(BaseModel):
    id: str
    name: str
    content_type: ContentType
    status: ContentStatus
    priority: Priority
    updated: str
    updated_at: datetime
    thumbnail_url: Optional[str] = None
    file_size_mb: Optional[float] = None
    duration_minutes: Optional[int] = None

# ============= CONTENT MODELS =============

class ContentItem(BaseModel):
    id: str
    name: str
    content_type: ContentType
    status: ContentStatus
    priority: Priority
    description: Optional[str] = None
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[int] = None
    thumbnail_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    uploaded_at: Optional[datetime] = None

class Movie(BaseModel):
    id: str
    title: str
    genre: str
    release_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    description: Optional[str] = None
    director: Optional[str] = None
    cast: Optional[List[str]] = None
    rating: Optional[str] = None
    language: Optional[str] = None
    country: Optional[str] = None
    poster_url: Optional[str] = None
    trailer_url: Optional[str] = None
    status: ContentStatus
    created_at: datetime
    updated_at: datetime

# ============= REQUEST MODELS =============

class ContentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    content_type: ContentType
    priority: Priority = Priority.MEDIUM
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

class ContentUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    content_type: Optional[ContentType] = None
    priority: Optional[Priority] = None
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class StatusUpdateRequest(BaseModel):
    status: ContentStatus

class MovieCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    genre: str = Field(..., min_length=1, max_length=100)
    release_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=2000)
    director: Optional[str] = Field(None, max_length=255)
    cast: Optional[List[str]] = None
    rating: Optional[str] = Field(None, max_length=10)
    language: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, max_length=100)

class BulkUpdateRequest(BaseModel):
    content_ids: List[str] = Field(..., min_items=1)
    updates: Dict[str, Any]

class BulkUpdateResult(BaseModel):
    updated_count: int
    failed_count: int
    errors: List[Dict[str, str]]

# ============= FILTER MODELS =============

class ContentFilters(BaseModel):
    status: Optional[str] = None
    content_type: Optional[str] = None
    priority: Optional[str] = None
    search: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None

class MovieFilters(BaseModel):
    genre: Optional[str] = None
    status: Optional[str] = None
    search: Optional[str] = None
    release_year: Optional[int] = None
    language: Optional[str] = None

# ============= UPLOAD MODELS =============

class UploadResult(BaseModel):
    upload_id: str
    file_name: str
    file_size_bytes: int
    content_type: str
    status: UploadStatus
    created_at: datetime

class UploadStatusInfo(BaseModel):
    upload_id: str
    status: UploadStatus
    progress_percentage: float
    file_name: str
    file_size_bytes: int
    bytes_uploaded: int
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

class FileValidationResult(BaseModel):
    is_valid: bool
    error_message: Optional[str] = None
    file_size_mb: Optional[float] = None
    file_extension: Optional[str] = None

# ============= ANALYTICS MODELS =============

class AnalyticsOverview(BaseModel):
    total_content: int
    content_by_status: Dict[str, int]
    content_by_type: Dict[str, int]
    content_by_priority: Dict[str, int]
    upload_trends: List[Dict[str, Any]]
    storage_trends: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]

class TrendData(BaseModel):
    labels: List[str]
    values: List[float]
    metric_name: str
    timeframe: str

class ReportRequest(BaseModel):
    report_type: str = Field(..., regex="^(summary|detailed|custom)$")
    timeframe: str = Field(..., regex="^(1d|7d|30d|90d)$")
    filters: Optional[Dict[str, Any]] = None
    format: ExportFormat = ExportFormat.JSON
    include_charts: bool = False

# ============= UTILITY MODELS =============

class CleanupRequest(BaseModel):
    older_than_days: int = Field(..., gt=0)
    include_failed_uploads: bool = True
    include_orphaned_files: bool = True
    dry_run: bool = False

class CleanupResult(BaseModel):
    files_deleted: int
    space_freed_gb: float
    errors: List[str]

# ============= PAGINATED RESPONSES =============

class PaginatedResult(BaseModel):
    items: List[Any]
    pagination: PaginationInfo

class ContentListResult(BaseModel):
    items: List[ContentItem]
    pagination: PaginationInfo

class MoviesListResult(BaseModel):
    items: List[Movie]
    pagination: PaginationInfo

# ============= API RESPONSE MODELS =============

class DashboardMetricsResponse(BaseResponse):
    data: DashboardMetrics

class StatusDistributionResponse(BaseResponse):
    data: StatusDistribution

class PriorityDistributionResponse(BaseResponse):
    data: PriorityDistribution

class RecentActivityResponse(BaseResponse):
    data: List[RecentActivity]

class StorageStatsResponse(BaseResponse):
    data: StorageStats

class ContentResponse(BaseResponse):
    data: ContentItem

class ContentListResponse(BaseResponse):
    data: List[ContentItem]
    pagination: PaginationInfo

class MovieResponse(BaseResponse):
    data: Movie

class MoviesListResponse(BaseResponse):
    data: List[Movie]
    pagination: PaginationInfo

class UploadResponse(BaseResponse):
    data: UploadResult

class BulkUploadResponse(BaseResponse):
    upload_id: str

class UploadStatusResponse(BaseResponse):
    data: UploadStatusInfo

class AnalyticsOverviewResponse(BaseResponse):
    data: AnalyticsOverview

class TrendsResponse(BaseResponse):
    data: TrendData

class ReportResponse(BaseResponse):
    report_id: str

class StatusUpdateResponse(BaseResponse):
    pass

class DeleteResponse(BaseResponse):
    pass

class BulkUpdateResponse(BaseResponse):
    data: BulkUpdateResult

class RefreshResponse(BaseResponse):
    pass

class CleanupResponse(BaseResponse):
    cleanup_id: str

class ExportResponse(BaseResponse):
    export_id: str

# ============= CONFIGURATION MODELS =============

class APIError(Exception):
    def __init__(self, message: str, status_code: int = 500, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)