import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
from pathlib import Path

class ContentStatus(Enum):
    READY = "Ready"
    UPLOADED = "Uploaded" 
    IN_PROGRESS = "In Progress"
    NEW = "New"

class Priority(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class ContentType(Enum):
    MOVIE = "Movie"
    REEL = "Reel"
    TRAILER = "Trailer"

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class SecurityConfig:
    """Security-related configuration"""
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    api_key: str = os.getenv("API_KEY", "")
    jwt_secret: str = os.getenv("JWT_SECRET_KEY", "")
    csrf_enabled: bool = os.getenv("CSRF_ENABLED", "true").lower() == "true"
    session_timeout_minutes: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
    rate_limit_enabled: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))

@dataclass
class APIConfig:
    """API-related configuration"""
    base_url: str = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
    timeout: int = int(os.getenv("API_TIMEOUT", "30"))
    retry_attempts: int = int(os.getenv("API_RETRY_ATTEMPTS", "3"))
    retry_delay: float = float(os.getenv("API_RETRY_DELAY", "1.0"))
    
    def get_headers(self) -> Dict[str, str]:
        """Get default API headers"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': f'CineMitr-Dashboard/{os.getenv("APP_VERSION", "1.0.0")}'
        }
        
        # Add API key if available
        api_key = os.getenv("API_KEY")
        if api_key:
            headers['X-API-Key'] = api_key
        
        return headers

@dataclass
class FileUploadConfig:
    """File upload configuration"""
    upload_folder: str = os.getenv("UPLOAD_FOLDER", "uploads")
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    allowed_extensions: List[str] = field(default_factory=lambda: 
        os.getenv("ALLOWED_FILE_EXTENSIONS", "mp4,avi,mov,mkv,jpg,jpeg,png,pdf").split(",")
    )
    
    def __post_init__(self):
        # Create upload directory if it doesn't exist
        try:
            Path(self.upload_folder).mkdir(parents=True, exist_ok=True)
        except Exception:
            # If can't create directory, use default
            self.upload_folder = "uploads"

@dataclass
class CacheConfig:
    """Cache configuration"""
    cache_type: str = os.getenv("CACHE_TYPE", "simple")
    cache_timeout: int = int(os.getenv("CACHE_TIMEOUT", "300"))
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

@dataclass
class DashboardConfig:
    """Main dashboard configuration class"""
    # Application Info
    app_title: str = os.getenv("APP_NAME", "CineMitr - Content Management Dashboard")
    app_icon: str = "📽️"
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    environment: Environment = Environment(os.getenv("ENVIRONMENT", "development"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # UI Configuration
    brand_color: str = "#4F46E5"
    sidebar_width: int = 300
    chart_height: int = 300
    refresh_interval: int = 30
    
    # Feature Flags
    enable_analytics: bool = os.getenv("ENABLE_ANALYTICS", "true").lower() == "true"
    enable_file_upload: bool = os.getenv("ENABLE_FILE_UPLOAD", "true").lower() == "true"
    enable_export: bool = os.getenv("ENABLE_EXPORT", "true").lower() == "true"
    enable_import: bool = os.getenv("ENABLE_IMPORT", "true").lower() == "true"
    enable_metrics: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    
    # Nested configurations
    security: SecurityConfig = field(default_factory=SecurityConfig)
    api: APIConfig = field(default_factory=APIConfig)
    file_upload: FileUploadConfig = field(default_factory=FileUploadConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    
    # Color schemes
    status_colors: Dict[str, str] = field(default_factory=dict)
    priority_colors: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        # Initialize color schemes
        self.status_colors = {
            ContentStatus.READY.value: "#3B82F6",
            ContentStatus.UPLOADED.value: "#10B981", 
            ContentStatus.IN_PROGRESS.value: "#F59E0B",
            ContentStatus.NEW.value: "#EF4444"
        }
        
        self.priority_colors = {
            Priority.HIGH.value: "#EF4444",
            Priority.MEDIUM.value: "#F59E0B",
            Priority.LOW.value: "#10B981"
        }
        
        # Validate critical configurations in production
        try:
            if self.environment == Environment.PRODUCTION:
                self._validate_production_config()
        except Exception:
            # Skip validation in development mode
            pass
    
    def _validate_production_config(self):
        """Validate configuration for production environment"""
        critical_vars = [
            ("SECRET_KEY", self.security.secret_key),
            ("API_BASE_URL", self.api.base_url)
        ]
        
        missing_vars = []
        for var_name, var_value in critical_vars:
            if not var_value or var_value.startswith("dev-") or var_value == "your_":
                missing_vars.append(var_name)
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables for production: {', '.join(missing_vars)}"
            )
    
    def get_streamlit_config(self) -> Dict[str, any]:
        """Get Streamlit-specific configuration"""
        return {
            "page_title": self.app_title,
            "page_icon": self.app_icon,
            "layout": "wide",
            "initial_sidebar_state": "expanded"
        }
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment == Environment.DEVELOPMENT
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == Environment.PRODUCTION

# Navigation Menu Items
MENU_ITEMS = [
    {"icon": "📊", "label": "Dashboard", "key": "dashboard"},
    {"icon": "🎬", "label": "Movies", "key": "movies"},
    {"icon": "📄", "label": "Content Items", "key": "content_items"},
    {"icon": "⬆️", "label": "Upload Pipeline", "key": "upload_pipeline"},
    {"icon": "📈", "label": "Analytics", "key": "analytics"},
    {"icon": "⚙️", "label": "Settings", "key": "settings"}
]

# Quick Action Buttons
QUICK_ACTIONS = [
    {"icon": "🔄", "label": "Refresh Data", "action": "refresh_data", "tooltip": "Refresh dashboard data"},
    {"icon": "📥", "label": "Import Data", "action": "import_data", "tooltip": "Import content from file"},
    {"icon": "➕", "label": "Add Content", "action": "add_content", "tooltip": "Add new content item"}
]

# Default pagination settings
PAGINATION_CONFIG = {
    "default_page_size": 20,
    "max_page_size": 100,
    "page_size_options": [10, 20, 50, 100]
}

# Chart configuration
CHART_CONFIG = {
    "pie_chart": {
        "textposition": "inside",
        "textinfo": "percent+label",
        "showlegend": True
    },
    "bar_chart": {
        "showlegend": False,
        "text_position": "outside"
    }
}

def load_config() -> DashboardConfig:
    """Load and return the dashboard configuration"""
    return DashboardConfig()

def get_database_url() -> str:
    """Get database URL for optional local database"""
    return os.getenv("DATABASE_URL", "sqlite:///./cinemitr.db")

def get_log_level() -> str:
    """Get logging level from environment"""
    return os.getenv("LOG_LEVEL", "INFO").upper()