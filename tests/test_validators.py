"""
Test cases for data validation utilities
"""

import pytest
from datetime import datetime
from utils.validators import DataValidator, ContentValidator
from utils.exceptions import ValidationException


class TestDataValidator:
    """Test suite for DataValidator class"""
    
    def test_validate_required_fields_success(self):
        """Test successful required field validation"""
        data = {"name": "Test", "email": "test@example.com", "age": 25}
        required_fields = ["name", "email"]
        
        # Should not raise exception
        DataValidator.validate_required_fields(data, required_fields)
    
    def test_validate_required_fields_missing(self):
        """Test required field validation with missing fields"""
        data = {"name": "Test"}
        required_fields = ["name", "email", "age"]
        
        with pytest.raises(ValidationException) as exc_info:
            DataValidator.validate_required_fields(data, required_fields)
        
        assert "Missing required fields" in str(exc_info.value)
        assert "email" in str(exc_info.value)
        assert "age" in str(exc_info.value)
    
    def test_validate_required_fields_empty(self):
        """Test required field validation with empty fields"""
        data = {"name": "", "email": "  ", "age": None}
        required_fields = ["name", "email", "age"]
        
        with pytest.raises(ValidationException) as exc_info:
            DataValidator.validate_required_fields(data, required_fields)
        
        assert "Empty required fields" in str(exc_info.value)
    
    def test_validate_string_length_success(self):
        """Test successful string length validation"""
        # Should not raise exception
        DataValidator.validate_string_length("Hello", "name", min_length=3, max_length=10)
    
    def test_validate_string_length_too_short(self):
        """Test string length validation with too short string"""
        with pytest.raises(ValidationException) as exc_info:
            DataValidator.validate_string_length("Hi", "name", min_length=5)
        
        assert "at least 5 characters" in str(exc_info.value)
    
    def test_validate_string_length_too_long(self):
        """Test string length validation with too long string"""
        with pytest.raises(ValidationException) as exc_info:
            DataValidator.validate_string_length("Very long string", "name", max_length=10)
        
        assert "must not exceed 10 characters" in str(exc_info.value)
    
    def test_validate_string_length_not_string(self):
        """Test string length validation with non-string input"""
        with pytest.raises(ValidationException) as exc_info:
            DataValidator.validate_string_length(123, "name")
        
        assert "must be a string" in str(exc_info.value)
    
    def test_validate_email_success(self):
        """Test successful email validation"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        
        for email in valid_emails:
            # Should not raise exception
            DataValidator.validate_email(email)
    
    def test_validate_email_failure(self):
        """Test email validation failure"""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com"
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValidationException) as exc_info:
                DataValidator.validate_email(email)
            assert "Invalid email format" in str(exc_info.value)
    
    def test_validate_url_success(self):
        """Test successful URL validation"""
        valid_urls = [
            "http://example.com",
            "https://www.example.com",
            "https://example.com/path?param=value",
            "http://localhost:8000"
        ]
        
        for url in valid_urls:
            # Should not raise exception
            DataValidator.validate_url(url)
    
    def test_validate_url_failure(self):
        """Test URL validation failure"""
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",
            "example.com"
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValidationException) as exc_info:
                DataValidator.validate_url(url)
            assert "Invalid URL format" in str(exc_info.value)
    
    def test_validate_choice_success(self):
        """Test successful choice validation"""
        choices = ["red", "green", "blue"]
        
        # Should not raise exception
        DataValidator.validate_choice("red", "color", choices)
    
    def test_validate_choice_failure(self):
        """Test choice validation failure"""
        choices = ["red", "green", "blue"]
        
        with pytest.raises(ValidationException) as exc_info:
            DataValidator.validate_choice("yellow", "color", choices)
        
        assert "must be one of" in str(exc_info.value)
        assert "red, green, blue" in str(exc_info.value)
    
    def test_validate_integer_range_success(self):
        """Test successful integer range validation"""
        # Should not raise exception
        DataValidator.validate_integer_range(5, "age", min_value=0, max_value=100)
        DataValidator.validate_integer_range("10", "count", min_value=0)  # String conversion
    
    def test_validate_integer_range_failure(self):
        """Test integer range validation failure"""
        with pytest.raises(ValidationException) as exc_info:
            DataValidator.validate_integer_range(-5, "age", min_value=0)
        assert "must be at least 0" in str(exc_info.value)
        
        with pytest.raises(ValidationException) as exc_info:
            DataValidator.validate_integer_range(150, "age", max_value=100)
        assert "must not exceed 100" in str(exc_info.value)
    
    def test_validate_float_range_success(self):
        """Test successful float range validation"""
        # Should not raise exception
        DataValidator.validate_float_range(3.14, "pi", min_value=0.0, max_value=10.0)
        DataValidator.validate_float_range("2.5", "value", min_value=0.0)  # String conversion
    
    def test_validate_datetime_success(self):
        """Test successful datetime validation"""
        # Should not raise exception and return datetime object
        result = DataValidator.validate_datetime("2023-12-25 10:30:00", "date")
        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 12
        assert result.day == 25
    
    def test_validate_datetime_with_datetime_object(self):
        """Test datetime validation with datetime object input"""
        dt = datetime(2023, 12, 25, 10, 30, 0)
        result = DataValidator.validate_datetime(dt, "date")
        assert result == dt
    
    def test_validate_datetime_failure(self):
        """Test datetime validation failure"""
        with pytest.raises(ValidationException) as exc_info:
            DataValidator.validate_datetime("invalid-date", "date")
        assert "must be in format" in str(exc_info.value)
    
    def test_sanitize_html(self):
        """Test HTML sanitization"""
        dangerous_html = '<script>alert("xss")</script><p>Safe content</p><iframe src="evil"></iframe>'
        sanitized = DataValidator.sanitize_html(dangerous_html)
        
        assert '<script>' not in sanitized
        assert '<iframe>' not in sanitized
        assert 'Safe content' in sanitized
    
    def test_validate_file_upload_success(self):
        """Test successful file upload validation"""
        # Mock file object
        class MockFile:
            def __init__(self, name, size):
                self.name = name
                self.size = size
        
        file_data = MockFile("test.jpg", 1024 * 1024)  # 1MB
        allowed_extensions = ["jpg", "png", "gif"]
        
        # Should not raise exception
        DataValidator.validate_file_upload(file_data, allowed_extensions, max_size_mb=10)
    
    def test_validate_file_upload_wrong_extension(self):
        """Test file upload validation with wrong extension"""
        class MockFile:
            def __init__(self, name, size):
                self.name = name
                self.size = size
        
        file_data = MockFile("test.txt", 1024)
        allowed_extensions = ["jpg", "png"]
        
        with pytest.raises(ValidationException) as exc_info:
            DataValidator.validate_file_upload(file_data, allowed_extensions)
        assert "File type not allowed" in str(exc_info.value)
    
    def test_validate_file_upload_too_large(self):
        """Test file upload validation with file too large"""
        class MockFile:
            def __init__(self, name, size):
                self.name = name
                self.size = size
        
        file_data = MockFile("test.jpg", 20 * 1024 * 1024)  # 20MB
        allowed_extensions = ["jpg"]
        
        with pytest.raises(ValidationException) as exc_info:
            DataValidator.validate_file_upload(file_data, allowed_extensions, max_size_mb=10)
        assert "File size exceeds" in str(exc_info.value)


class TestContentValidator:
    """Test suite for ContentValidator class"""
    
    def test_validate_content_item_success(self):
        """Test successful content item validation"""
        data = {
            "name": "Test Movie",
            "content_type": "Movie",
            "status": "New",
            "priority": "High",
            "description": "A test movie description"
        }
        
        # Should not raise exception
        ContentValidator.validate_content_item(data)
    
    def test_validate_content_item_missing_required(self):
        """Test content item validation with missing required fields"""
        data = {
            "name": "Test Movie",
            # Missing required fields
        }
        
        with pytest.raises(ValidationException) as exc_info:
            ContentValidator.validate_content_item(data)
        assert "Missing required fields" in str(exc_info.value)
    
    def test_validate_content_item_invalid_choice(self):
        """Test content item validation with invalid choices"""
        data = {
            "name": "Test Movie",
            "content_type": "InvalidType",  # Invalid choice
            "status": "New",
            "priority": "High"
        }
        
        with pytest.raises(ValidationException) as exc_info:
            ContentValidator.validate_content_item(data)
        assert "must be one of" in str(exc_info.value)
    
    def test_validate_movie_data_success(self):
        """Test successful movie data validation"""
        data = {
            "title": "Test Movie",
            "genre": "Action",
            "duration": 120,
            "release_date": "2023-12-25"
        }
        
        # Should not raise exception
        ContentValidator.validate_movie_data(data)
    
    def test_validate_movie_data_invalid_duration(self):
        """Test movie data validation with invalid duration"""
        data = {
            "title": "Test Movie",
            "genre": "Action",
            "duration": -10  # Invalid duration
        }
        
        with pytest.raises(ValidationException) as exc_info:
            ContentValidator.validate_movie_data(data)
        assert "must be at least 1" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__])