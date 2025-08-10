"""
API endpoints configuration for CineMitr Dashboard
This file contains all the API endpoint definitions that will be used by the APIService class.
"""

from dataclasses import dataclass
from typing import Dict

@dataclass
class APIEndpoints:
    """API endpoint configuration class"""
    BASE_URL: str = "http://localhost:8000/api/v1"
    
    # Dashboard endpoints
    METRICS: str = "/dashboard/metrics"
    STATUS_DISTRIBUTION: str = "/dashboard/status-distribution"
    PRIORITY_DISTRIBUTION: str = "/dashboard/priority-distribution"
    RECENT_ACTIVITY: str = "/dashboard/recent-activity"
    
    # Content management endpoints
    CONTENT_LIST: str = "/content"
    CONTENT_CREATE: str = "/content"
    CONTENT_DETAIL: str = "/content/{id}"
    CONTENT_UPDATE: str = "/content/{id}"
    CONTENT_DELETE: str = "/content/{id}"
    CONTENT_STATUS_UPDATE: str = "/content/{id}/status"
    
    # Movies endpoints
    MOVIES_LIST: str = "/movies"
    MOVIES_CREATE: str = "/movies"
    MOVIES_DETAIL: str = "/movies/{id}"
    MOVIES_UPDATE: str = "/movies/{id}"
    MOVIES_DELETE: str = "/movies/{id}"
    MOVIES_IMPORT: str = "/movies/import"
    MOVIES_EXPORT: str = "/movies/export"
    
    # Upload endpoints
    UPLOAD_FILE: str = "/upload"
    UPLOAD_STATUS: str = "/upload/{upload_id}/status"
    UPLOAD_PROGRESS: str = "/upload/{upload_id}/progress"
    
    # Analytics endpoints
    ANALYTICS_OVERVIEW: str = "/analytics/overview"
    ANALYTICS_REPORT: str = "/analytics/report"
    ANALYTICS_EXPORT: str = "/analytics/export"
    
    # Settings endpoints
    SETTINGS_GET: str = "/settings"
    SETTINGS_UPDATE: str = "/settings"
    USER_PREFERENCES: str = "/user/preferences"
    
    # Authentication endpoints (if needed)
    LOGIN: str = "/auth/login"
    LOGOUT: str = "/auth/logout"
    REFRESH_TOKEN: str = "/auth/refresh"
    
    def get_full_url(self, endpoint: str, **kwargs) -> str:
        """Get full URL for an endpoint with optional parameters"""
        if kwargs:
            endpoint = endpoint.format(**kwargs)
        return f"{self.BASE_URL}{endpoint}"

# HTTP Methods configuration
HTTP_METHODS = {
    "GET": "GET",
    "POST": "POST", 
    "PUT": "PUT",
    "PATCH": "PATCH",
    "DELETE": "DELETE"
}

# API Request/Response models (for reference when implementing actual APIs)
API_MODELS = {
    "dashboard_metrics": {
        "response": {
            "total_movies": "integer",
            "content_items": "integer", 
            "uploaded": "integer",
            "uploaded_weekly_change": "integer",
            "pending": "integer",
            "upload_rate": "float"
        }
    },
    "content_item": {
        "request": {
            "name": "string",
            "content_type": "string",
            "status": "string",
            "priority": "string",
            "description": "string (optional)"
        },
        "response": {
            "id": "string",
            "name": "string", 
            "content_type": "string",
            "status": "string",
            "priority": "string",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    },
    "movie": {
        "request": {
            "title": "string",
            "genre": "string",
            "release_date": "date",
            "duration": "integer (minutes)",
            "description": "string"
        },
        "response": {
            "id": "string",
            "title": "string",
            "genre": "string", 
            "release_date": "date",
            "duration": "integer",
            "description": "string",
            "status": "string",
            "created_at": "datetime"
        }
    }
}