"""
CineMitr Content Management Dashboard - FastAPI Backend
This is the main FastAPI application with all backend endpoints
"""

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uvicorn
import os
import json
import asyncio
from pathlib import Path

# Import our models and services
from models import *
from services.dashboard_service import DashboardService
from services.content_service import ContentService
try:
    from services.upload_service import UploadService
except ImportError:
    from services.upload_service_simple import UploadService
try:
    from services.analytics_service import AnalyticsService
except ImportError:
    from services.analytics_service_simple import AnalyticsService
try:
    from services.storage_service import StorageService
except ImportError:
    from services.storage_service_simple import StorageService
from database.connection import db_manager
from config import DashboardConfig
from utils.logger import setup_logger
try:
    from utils.validators import validate_file_upload
except ImportError:
    from utils.validators_simple import validate_file_upload
from utils.exceptions import APIError

# Initialize configuration and logger
config = DashboardConfig()
logger = setup_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CineMitr Content Management API",
    description="Backend API for CineMitr Content Management Dashboard",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Initialize services
dashboard_service = DashboardService()
content_service = ContentService()
upload_service = UploadService()
analytics_service = AnalyticsService()
storage_service = StorageService()

# Dependency to get current user (if authentication is needed)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials and config.environment.value == "production":
        raise HTTPException(status_code=401, detail="Authentication required")
    return {"user_id": "admin-001"}  # Mock admin user for now

# Database dependency
def get_db():
    """Get database session dependency"""
    return db_manager.get_session()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting CineMitr API server...")
    
    # Initialize database connection
    try:
        db_manager.initialize()
        logger.info("Database connection initialized")
        
        # Test database connection
        if db_manager.test_connection():
            logger.info("Database connection test successful")
        else:
            logger.error("Database connection test failed")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        # Continue without database for development
    
    # Initialize services
    await dashboard_service.initialize()
    await content_service.initialize()
    await upload_service.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down CineMitr API server...")

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=config.app_version,
        environment=config.environment.value
    )

# ============= DASHBOARD ENDPOINTS =============

@app.get("/api/v1/dashboard/metrics", response_model=DashboardMetricsResponse)
async def get_dashboard_metrics(user = Depends(get_current_user)):
    """Get dashboard metrics with trends and real-time data"""
    try:
        metrics = await dashboard_service.get_metrics()
        return DashboardMetricsResponse(
            success=True,
            data=metrics,
            message="Dashboard metrics retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching dashboard metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard metrics")

@app.get("/api/v1/dashboard/status-distribution", response_model=StatusDistributionResponse)
async def get_status_distribution(user = Depends(get_current_user)):
    """Get content status distribution for pie chart"""
    try:
        distribution = await dashboard_service.get_status_distribution()
        return StatusDistributionResponse(
            success=True,
            data=distribution,
            message="Status distribution retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching status distribution: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch status distribution")

@app.get("/api/v1/dashboard/priority-distribution", response_model=PriorityDistributionResponse)
async def get_priority_distribution(user = Depends(get_current_user)):
    """Get priority distribution for bar chart"""
    try:
        distribution = await dashboard_service.get_priority_distribution()
        return PriorityDistributionResponse(
            success=True,
            data=distribution,
            message="Priority distribution retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching priority distribution: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch priority distribution")

@app.get("/api/v1/dashboard/recent-activity", response_model=RecentActivityResponse)
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=100),
    user = Depends(get_current_user)
):
    """Get recent activity with metadata and thumbnails"""
    try:
        activities = await dashboard_service.get_recent_activity(limit)
        return RecentActivityResponse(
            success=True,
            data=activities,
            message="Recent activity retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching recent activity: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch recent activity")

@app.get("/api/v1/dashboard/storage-stats", response_model=StorageStatsResponse)
async def get_storage_stats(user = Depends(get_current_user)):
    """Get storage usage statistics"""
    try:
        stats = await storage_service.get_storage_stats()
        return StorageStatsResponse(
            success=True,
            data=stats,
            message="Storage statistics retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching storage stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch storage statistics")

# ============= CONTENT MANAGEMENT ENDPOINTS =============

@app.get("/api/v1/content", response_model=ContentListResponse)
async def get_content_list(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    content_type: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    user = Depends(get_current_user)
):
    """Get paginated content list with filtering"""
    try:
        filters = ContentFilters(
            status=status,
            content_type=content_type,
            priority=priority,
            search=search
        )
        result = await content_service.get_content_list(page, limit, filters)
        return ContentListResponse(
            success=True,
            data=result.items,
            pagination=result.pagination,
            message="Content list retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching content list: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch content list")

@app.post("/api/v1/content", response_model=ContentResponse)
async def create_content(
    content_data: ContentCreateRequest,
    user = Depends(get_current_user)
):
    """Create new content item"""
    try:
        content = await content_service.create_content(content_data)
        return ContentResponse(
            success=True,
            data=content,
            message="Content created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating content: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create content")

@app.get("/api/v1/content/{content_id}", response_model=ContentResponse)
async def get_content_detail(
    content_id: str,
    user = Depends(get_current_user)
):
    """Get content item details"""
    try:
        content = await content_service.get_content_by_id(content_id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        return ContentResponse(
            success=True,
            data=content,
            message="Content details retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching content details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch content details")

@app.put("/api/v1/content/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: str,
    content_data: ContentUpdateRequest,
    user = Depends(get_current_user)
):
    """Update content item"""
    try:
        content = await content_service.update_content(content_id, content_data)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        return ContentResponse(
            success=True,
            data=content,
            message="Content updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating content: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update content")

@app.patch("/api/v1/content/{content_id}/status", response_model=StatusUpdateResponse)
async def update_content_status(
    content_id: str,
    status_data: StatusUpdateRequest,
    user = Depends(get_current_user)
):
    """Update content status"""
    try:
        result = await content_service.update_status(content_id, status_data.status)
        if not result:
            raise HTTPException(status_code=404, detail="Content not found")
        return StatusUpdateResponse(
            success=True,
            message=f"Content status updated to {status_data.status}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating content status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update content status")

@app.delete("/api/v1/content/{content_id}", response_model=DeleteResponse)
async def delete_content(
    content_id: str,
    user = Depends(get_current_user)
):
    """Delete content item"""
    try:
        result = await content_service.delete_content(content_id)
        if not result:
            raise HTTPException(status_code=404, detail="Content not found")
        return DeleteResponse(
            success=True,
            message="Content deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting content: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete content")

@app.post("/api/v1/content/bulk-update", response_model=BulkUpdateResponse)
async def bulk_update_content(
    bulk_data: BulkUpdateRequest,
    user = Depends(get_current_user)
):
    """Bulk update multiple content items"""
    try:
        result = await content_service.bulk_update(bulk_data.content_ids, bulk_data.updates)
        return BulkUpdateResponse(
            success=True,
            data=result,
            message=f"Successfully updated {result.updated_count} items"
        )
    except Exception as e:
        logger.error(f"Error in bulk update: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to perform bulk update")

# ============= MOVIES ENDPOINTS =============

@app.get("/api/v1/movies", response_model=MoviesListResponse)
async def get_movies_list(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    genre: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    user = Depends(get_current_user)
):
    """Get paginated movies list with filtering"""
    try:
        filters = MovieFilters(
            genre=genre,
            status=status,
            search=search
        )
        result = await content_service.get_movies_list(page, limit, filters)
        return MoviesListResponse(
            success=True,
            data=result.items,
            pagination=result.pagination,
            message="Movies list retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching movies list: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch movies list")

@app.post("/api/v1/movies", response_model=MovieResponse)
async def create_movie(
    movie_data: MovieCreateRequest,
    user = Depends(get_current_user)
):
    """Create new movie"""
    try:
        movie = await content_service.create_movie(movie_data)
        return MovieResponse(
            success=True,
            data=movie,
            message="Movie created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating movie: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create movie")

@app.put("/api/v1/movies/{movie_id}", response_model=MovieResponse)
async def update_movie(
    movie_id: str,
    movie_data: MovieCreateRequest,
    user = Depends(get_current_user)
):
    """Update existing movie"""
    try:
        movie = await content_service.update_movie(movie_id, movie_data)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        return MovieResponse(
            success=True,
            data=movie,
            message="Movie updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating movie: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update movie")

@app.delete("/api/v1/movies/{movie_id}", response_model=DeleteResponse)
async def delete_movie(
    movie_id: str,
    user = Depends(get_current_user)
):
    """Delete movie"""
    try:
        success = await content_service.delete_movie(movie_id)
        if not success:
            raise HTTPException(status_code=404, detail="Movie not found")
        return DeleteResponse(
            success=True,
            message="Movie deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting movie: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete movie")

@app.get("/api/v1/movies/{movie_id}", response_model=MovieResponse)
async def get_movie_details(
    movie_id: str,
    user = Depends(get_current_user)
):
    """Get movie details by ID"""
    try:
        movie = await content_service.get_movie_by_id(movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        return MovieResponse(
            success=True,
            data=movie,
            message="Movie details retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching movie details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch movie details")

# ============= UPLOAD ENDPOINTS =============

@app.post("/api/v1/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    content_type: str = Query(...),
    priority: str = Query("Medium"),
    user = Depends(get_current_user)
):
    """Upload a file with metadata"""
    try:
        # Validate file
        validation_result = await validate_file_upload(file, config.file_upload)
        if not validation_result.is_valid:
            raise HTTPException(status_code=400, detail=validation_result.error_message)
        
        # Process upload
        upload_result = await upload_service.upload_file(file, content_type, priority)
        return UploadResponse(
            success=True,
            data=upload_result,
            message="File uploaded successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload file")

@app.post("/api/v1/upload/bulk", response_model=BulkUploadResponse)
async def bulk_upload_files(
    files: List[UploadFile] = File(...),
    content_type: str = Query(...),
    priority: str = Query("Medium"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    user = Depends(get_current_user)
):
    """Bulk upload multiple files"""
    try:
        upload_id = await upload_service.start_bulk_upload(files, content_type, priority)
        background_tasks.add_task(upload_service.process_bulk_upload, upload_id)
        
        return BulkUploadResponse(
            success=True,
            upload_id=upload_id,
            message=f"Bulk upload started for {len(files)} files"
        )
    except Exception as e:
        logger.error(f"Error starting bulk upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start bulk upload")

@app.get("/api/v1/upload/{upload_id}/status", response_model=UploadStatusResponse)
async def get_upload_status(
    upload_id: str,
    user = Depends(get_current_user)
):
    """Get upload status and progress"""
    try:
        status = await upload_service.get_upload_status(upload_id)
        if not status:
            raise HTTPException(status_code=404, detail="Upload not found")
        return UploadStatusResponse(
            success=True,
            data=status,
            message="Upload status retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching upload status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch upload status")

# ============= ANALYTICS ENDPOINTS =============

@app.get("/api/v1/analytics/overview", response_model=AnalyticsOverviewResponse)
async def get_analytics_overview(
    timeframe: str = Query("7d", regex="^(1d|7d|30d|90d)$"),
    user = Depends(get_current_user)
):
    """Get analytics overview with trends and insights"""
    try:
        overview = await analytics_service.get_overview(timeframe)
        return AnalyticsOverviewResponse(
            success=True,
            data=overview,
            message="Analytics overview retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching analytics overview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics overview")

@app.get("/api/v1/analytics/trends", response_model=TrendsResponse)
async def get_analytics_trends(
    metric: str = Query(...),
    timeframe: str = Query("7d"),
    user = Depends(get_current_user)
):
    """Get trend data for specific metrics"""
    try:
        trends = await analytics_service.get_trends(metric, timeframe)
        return TrendsResponse(
            success=True,
            data=trends,
            message="Trends data retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching trends: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch trends data")

@app.post("/api/v1/analytics/report", response_model=ReportResponse)
async def generate_analytics_report(
    report_request: ReportRequest,
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user)
):
    """Generate analytics report"""
    try:
        report_id = await analytics_service.start_report_generation(report_request)
        background_tasks.add_task(analytics_service.generate_report, report_id)
        
        return ReportResponse(
            success=True,
            report_id=report_id,
            message="Report generation started"
        )
    except Exception as e:
        logger.error(f"Error starting report generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start report generation")

# ============= UTILITY ENDPOINTS =============

@app.post("/api/v1/refresh", response_model=RefreshResponse)
async def refresh_data(user = Depends(get_current_user)):
    """Refresh all cached data"""
    try:
        await dashboard_service.refresh_cache()
        await content_service.refresh_cache()
        await analytics_service.refresh_cache()
        
        return RefreshResponse(
            success=True,
            message="Data refreshed successfully"
        )
    except Exception as e:
        logger.error(f"Error refreshing data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to refresh data")

@app.post("/api/v1/cleanup", response_model=CleanupResponse)
async def cleanup_data(
    cleanup_request: CleanupRequest,
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user)
):
    """Cleanup old data and files"""
    try:
        cleanup_id = await storage_service.start_cleanup(cleanup_request)
        background_tasks.add_task(storage_service.perform_cleanup, cleanup_id)
        
        return CleanupResponse(
            success=True,
            cleanup_id=cleanup_id,
            message="Cleanup started"
        )
    except Exception as e:
        logger.error(f"Error starting cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start cleanup")

@app.get("/api/v1/export/{format}", response_model=ExportResponse)
async def export_data(
    format: str,
    content_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    user = Depends(get_current_user)
):
    """Export data in various formats"""
    try:
        if format not in ["csv", "json", "xlsx"]:
            raise HTTPException(status_code=400, detail="Unsupported export format")
        
        export_id = await content_service.start_export(format, content_type, status)
        background_tasks.add_task(content_service.generate_export, export_id)
        
        return ExportResponse(
            success=True,
            export_id=export_id,
            message=f"Export to {format.upper()} started"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting export: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start export")

@app.get("/api/v1/download/{file_id}")
async def download_file(file_id: str, user = Depends(get_current_user)):
    """Download exported file or content"""
    try:
        # Get file path from content service export registry
        file_path = content_service.get_export_file_path(file_id)
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine media type based on file extension
        filename = os.path.basename(file_path)
        media_type = "application/octet-stream"
        if filename.endswith('.csv'):
            media_type = "text/csv"
        elif filename.endswith('.json'):
            media_type = "application/json"
        elif filename.endswith('.xlsx'):
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        return FileResponse(
            file_path,
            media_type=media_type,
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download file")

# Error handlers
@app.exception_handler(APIError)
async def api_error_handler(request, exc: APIError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.message, "error_code": exc.error_code}
    )

@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"success": False, "message": str(exc)}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.debug,
        log_level="info"
    )