"""
Test cases for configuration management
"""

import os
import pytest
from unittest.mock import patch
from config import (
    DashboardConfig, SecurityConfig, APIConfig, FileUploadConfig,
    ContentStatus, Priority, ContentType, Environment
)


class TestDashboardConfig:
    """Test suite for DashboardConfig class"""
    
    def test_default_config_creation(self):
        """Test default configuration creation"""
        config = DashboardConfig()
        
        assert config.app_title == "CineMitr - Content Management Dashboard"
        assert config.app_icon == "📽️"
        assert config.environment == Environment.DEVELOPMENT
        assert config.debug == False
        assert config.enable_analytics == True
    
    @patch.dict(os.environ, {
        'APP_NAME': 'Test Dashboard',
        'DEBUG': 'true',
        'ENABLE_ANALYTICS': 'false'
    })
    def test_config_from_environment(self):
        """Test configuration loading from environment variables"""
        config = DashboardConfig()
        
        assert config.app_title == "Test Dashboard"
        assert config.debug == True
        assert config.enable_analytics == False
    
    def test_color_scheme_initialization(self):
        """Test color scheme initialization"""
        config = DashboardConfig()
        
        assert ContentStatus.READY.value in config.status_colors
        assert Priority.HIGH.value in config.priority_colors
        assert config.status_colors[ContentStatus.READY.value] == "#3B82F6"
        assert config.priority_colors[Priority.HIGH.value] == "#EF4444"
    
    def test_streamlit_config(self):
        """Test Streamlit configuration generation"""
        config = DashboardConfig()
        streamlit_config = config.get_streamlit_config()
        
        assert "page_title" in streamlit_config
        assert "page_icon" in streamlit_config
        assert streamlit_config["layout"] == "wide"
    
    def test_environment_detection(self):
        """Test environment detection methods"""
        config = DashboardConfig()
        
        assert config.is_development() == True
        assert config.is_production() == False
    
    @patch.dict(os.environ, {
        'ENVIRONMENT': 'production',
        'SECRET_KEY': 'production-secret-key',
        'API_BASE_URL': 'https://api.production.com/v1'
    })
    def test_production_config_validation(self):
        """Test production configuration validation"""
        config = DashboardConfig()
        
        assert config.environment == Environment.PRODUCTION
        assert config.is_production() == True
    
    @patch.dict(os.environ, {
        'ENVIRONMENT': 'production',
        'SECRET_KEY': 'dev-secret-key',
        'API_BASE_URL': 'http://localhost:8000/api/v1'
    })
    def test_production_config_validation_failure(self):
        """Test production configuration validation failure"""
        with pytest.raises(ValueError) as exc_info:
            DashboardConfig()
        
        assert "Missing required environment variables" in str(exc_info.value)


class TestSecurityConfig:
    """Test suite for SecurityConfig class"""
    
    def test_default_security_config(self):
        """Test default security configuration"""
        security_config = SecurityConfig()
        
        assert security_config.secret_key == "dev-secret-key-change-in-production"
        assert security_config.csrf_enabled == True
        assert security_config.session_timeout_minutes == 60
        assert security_config.rate_limit_enabled == True
    
    @patch.dict(os.environ, {
        'SECRET_KEY': 'custom-secret',
        'CSRF_ENABLED': 'false',
        'SESSION_TIMEOUT_MINUTES': '120'
    })
    def test_security_config_from_env(self):
        """Test security configuration from environment"""
        security_config = SecurityConfig()
        
        assert security_config.secret_key == "custom-secret"
        assert security_config.csrf_enabled == False
        assert security_config.session_timeout_minutes == 120


class TestAPIConfig:
    """Test suite for APIConfig class"""
    
    def test_default_api_config(self):
        """Test default API configuration"""
        api_config = APIConfig()
        
        assert api_config.base_url == "http://localhost:8000/api/v1"
        assert api_config.timeout == 30
        assert api_config.retry_attempts == 3
        assert api_config.retry_delay == 1.0
    
    def test_api_headers_without_key(self):
        """Test API headers without API key"""
        api_config = APIConfig()
        headers = api_config.get_headers()
        
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        assert "User-Agent" in headers
        assert "X-API-Key" not in headers
    
    @patch.dict(os.environ, {'API_KEY': 'test-api-key'})
    def test_api_headers_with_key(self):
        """Test API headers with API key"""
        api_config = APIConfig()
        headers = api_config.get_headers()
        
        assert headers["X-API-Key"] == "test-api-key"
    
    @patch.dict(os.environ, {
        'API_BASE_URL': 'https://custom-api.com/v2',
        'API_TIMEOUT': '60',
        'API_RETRY_ATTEMPTS': '5'
    })
    def test_api_config_from_env(self):
        """Test API configuration from environment"""
        api_config = APIConfig()
        
        assert api_config.base_url == "https://custom-api.com/v2"
        assert api_config.timeout == 60
        assert api_config.retry_attempts == 5


class TestFileUploadConfig:
    """Test suite for FileUploadConfig class"""
    
    def test_default_file_upload_config(self):
        """Test default file upload configuration"""
        upload_config = FileUploadConfig()
        
        assert upload_config.upload_folder == "uploads"
        assert upload_config.max_file_size_mb == 50
        assert "mp4" in upload_config.allowed_extensions
        assert "pdf" in upload_config.allowed_extensions
    
    @patch.dict(os.environ, {
        'UPLOAD_FOLDER': 'custom_uploads',
        'MAX_FILE_SIZE_MB': '100',
        'ALLOWED_FILE_EXTENSIONS': 'jpg,png,gif'
    })
    def test_file_upload_config_from_env(self):
        """Test file upload configuration from environment"""
        upload_config = FileUploadConfig()
        
        assert upload_config.upload_folder == "custom_uploads"
        assert upload_config.max_file_size_mb == 100
        assert upload_config.allowed_extensions == ["jpg", "png", "gif"]


class TestEnums:
    """Test suite for configuration enums"""
    
    def test_content_status_enum(self):
        """Test ContentStatus enum values"""
        assert ContentStatus.READY.value == "Ready"
        assert ContentStatus.UPLOADED.value == "Uploaded"
        assert ContentStatus.IN_PROGRESS.value == "In Progress"
        assert ContentStatus.NEW.value == "New"
    
    def test_priority_enum(self):
        """Test Priority enum values"""
        assert Priority.HIGH.value == "High"
        assert Priority.MEDIUM.value == "Medium"
        assert Priority.LOW.value == "Low"
    
    def test_content_type_enum(self):
        """Test ContentType enum values"""
        assert ContentType.MOVIE.value == "Movie"
        assert ContentType.REEL.value == "Reel"
        assert ContentType.TRAILER.value == "Trailer"
    
    def test_environment_enum(self):
        """Test Environment enum values"""
        assert Environment.DEVELOPMENT.value == "development"
        assert Environment.STAGING.value == "staging"
        assert Environment.PRODUCTION.value == "production"


if __name__ == "__main__":
    pytest.main([__file__])