"""
Test cases for API service functionality
"""

import pytest
import requests
from unittest.mock import Mock, patch
from api_service import APIService, DashboardMetrics, StatusDistribution, PriorityDistribution, ContentItem
from config import DashboardConfig, ContentStatus, ContentType, Priority


@pytest.fixture
def config():
    """Test configuration fixture"""
    return DashboardConfig()


@pytest.fixture
def api_service(config):
    """API service fixture"""
    return APIService(config)


class TestAPIService:
    """Test suite for APIService class"""
    
    def test_init(self, api_service, config):
        """Test API service initialization"""
        assert api_service.config == config
        assert api_service.session is not None
        assert 'Content-Type' in api_service.session.headers
        assert api_service.session.headers['Content-Type'] == 'application/json'
    
    @patch('api_service.requests.Session.get')
    def test_get_dashboard_metrics_success(self, mock_get, api_service):
        """Test successful dashboard metrics retrieval"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "total_movies": 127,
            "content_items": 2847,
            "uploaded": 1923,
            "uploaded_weekly_change": 47,
            "pending": 234,
            "upload_rate": 67.5
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test the method
        metrics = api_service.get_dashboard_metrics()
        
        # Assertions
        assert isinstance(metrics, DashboardMetrics)
        assert metrics.total_movies == 127
        assert metrics.content_items == 2847
        assert metrics.upload_rate == 67.5
    
    @patch('api_service.requests.Session.get')
    def test_get_dashboard_metrics_error(self, mock_get, api_service):
        """Test dashboard metrics retrieval with API error"""
        # Mock API error
        mock_get.side_effect = requests.RequestException("API Error")
        
        # Test the method - should return default values on error
        metrics = api_service.get_dashboard_metrics()
        
        # Assertions
        assert isinstance(metrics, DashboardMetrics)
        assert metrics.total_movies == 0
        assert metrics.content_items == 0
    
    def test_get_status_distribution(self, api_service):
        """Test status distribution retrieval"""
        status_dist = api_service.get_status_distribution()
        
        assert isinstance(status_dist, StatusDistribution)
        assert status_dist.ready >= 0
        assert status_dist.uploaded >= 0
        assert status_dist.in_progress >= 0
        assert status_dist.new >= 0
    
    def test_get_priority_distribution(self, api_service):
        """Test priority distribution retrieval"""
        priority_dist = api_service.get_priority_distribution()
        
        assert isinstance(priority_dist, PriorityDistribution)
        assert priority_dist.high >= 0
        assert priority_dist.medium >= 0
        assert priority_dist.low >= 0
    
    def test_get_recent_activity(self, api_service):
        """Test recent activity retrieval"""
        activity = api_service.get_recent_activity()
        
        assert isinstance(activity, list)
        if activity:  # If there's data
            assert isinstance(activity[0], ContentItem)
            assert hasattr(activity[0], 'id')
            assert hasattr(activity[0], 'name')
            assert hasattr(activity[0], 'content_type')
    
    def test_refresh_data(self, api_service):
        """Test data refresh functionality"""
        result = api_service.refresh_data()
        assert isinstance(result, bool)
    
    @patch('api_service.requests.Session.post')
    def test_add_content_success(self, mock_post, api_service):
        """Test successful content addition"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success",
            "message": "Content added successfully",
            "id": "new_123"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        content_data = {
            "name": "Test Movie",
            "content_type": "Movie",
            "status": "New",
            "priority": "High"
        }
        
        result = api_service.add_content(content_data)
        
        assert result["status"] == "success"
        assert "id" in result
    
    @patch('api_service.requests.Session.patch')
    def test_update_content_status(self, mock_patch, api_service):
        """Test content status update"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success",
            "message": "Status updated"
        }
        mock_response.raise_for_status.return_value = None
        mock_patch.return_value = mock_response
        
        result = api_service.update_content_status("123", ContentStatus.READY)
        
        assert result["status"] == "success"
    
    @patch('api_service.requests.Session.delete')
    def test_delete_content(self, mock_delete, api_service):
        """Test content deletion"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success",
            "message": "Content deleted"
        }
        mock_response.raise_for_status.return_value = None
        mock_delete.return_value = mock_response
        
        result = api_service.delete_content("123")
        
        assert result["status"] == "success"


class TestDataModels:
    """Test suite for data model classes"""
    
    def test_dashboard_metrics_creation(self):
        """Test DashboardMetrics model creation"""
        metrics = DashboardMetrics(
            total_movies=100,
            content_items=500,
            uploaded=400,
            uploaded_weekly_change=25,
            pending=50,
            upload_rate=80.0
        )
        
        assert metrics.total_movies == 100
        assert metrics.upload_rate == 80.0
    
    def test_content_item_creation(self):
        """Test ContentItem model creation"""
        item = ContentItem(
            id="123",
            name="Test Movie",
            content_type=ContentType.MOVIE,
            status=ContentStatus.NEW,
            priority=Priority.HIGH,
            updated="2 hours ago"
        )
        
        assert item.id == "123"
        assert item.content_type == ContentType.MOVIE
        assert item.status == ContentStatus.NEW
        assert item.priority == Priority.HIGH
    
    def test_status_distribution_creation(self):
        """Test StatusDistribution model creation"""
        dist = StatusDistribution(ready=10, uploaded=20, in_progress=5, new=15)
        
        assert dist.ready == 10
        assert dist.uploaded == 20
        assert dist.in_progress == 5
        assert dist.new == 15
    
    def test_priority_distribution_creation(self):
        """Test PriorityDistribution model creation"""
        dist = PriorityDistribution(high=15, medium=25, low=10)
        
        assert dist.high == 15
        assert dist.medium == 25
        assert dist.low == 10


if __name__ == "__main__":
    pytest.main([__file__])