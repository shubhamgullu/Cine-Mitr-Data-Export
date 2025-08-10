"""
Data validation utilities for CineMitr Dashboard
Provides validation functions for user inputs and API data
"""

import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from utils.exceptions import ValidationException

class DataValidator:
    """Utility class for data validation"""
    
    # Regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
        """Validate that all required fields are present and not empty"""
        missing_fields = []
        empty_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
            elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
                empty_fields.append(field)
        
        if missing_fields:
            raise ValidationException(
                f"Missing required fields: {', '.join(missing_fields)}",
                context={"missing_fields": missing_fields}
            )
        
        if empty_fields:
            raise ValidationException(
                f"Empty required fields: {', '.join(empty_fields)}",
                context={"empty_fields": empty_fields}
            )
    
    @staticmethod
    def validate_string_length(value: str, field_name: str, min_length: int = 1, 
                             max_length: int = 255) -> None:
        """Validate string length constraints"""
        if not isinstance(value, str):
            raise ValidationException(
                f"{field_name} must be a string",
                field=field_name,
                value=value
            )
        
        if len(value) < min_length:
            raise ValidationException(
                f"{field_name} must be at least {min_length} characters long",
                field=field_name,
                value=value
            )
        
        if len(value) > max_length:
            raise ValidationException(
                f"{field_name} must not exceed {max_length} characters",
                field=field_name,
                value=value
            )
    
    @staticmethod
    def validate_email(email: str) -> None:
        """Validate email format"""
        if not isinstance(email, str) or not DataValidator.EMAIL_PATTERN.match(email):
            raise ValidationException(
                "Invalid email format",
                field="email",
                value=email
            )
    
    @staticmethod
    def validate_url(url: str) -> None:
        """Validate URL format"""
        if not isinstance(url, str) or not DataValidator.URL_PATTERN.match(url):
            raise ValidationException(
                "Invalid URL format",
                field="url",
                value=url
            )
    
    @staticmethod
    def validate_choice(value: Any, field_name: str, choices: List[Any]) -> None:
        """Validate that value is one of the allowed choices"""
        if value not in choices:
            raise ValidationException(
                f"{field_name} must be one of: {', '.join(map(str, choices))}",
                field=field_name,
                value=value,
                context={"allowed_choices": choices}
            )
    
    @staticmethod
    def validate_integer_range(value: Any, field_name: str, min_value: Optional[int] = None, 
                             max_value: Optional[int] = None) -> None:
        """Validate integer value and range"""
        if not isinstance(value, int):
            try:
                value = int(value)
            except (ValueError, TypeError):
                raise ValidationException(
                    f"{field_name} must be an integer",
                    field=field_name,
                    value=value
                )
        
        if min_value is not None and value < min_value:
            raise ValidationException(
                f"{field_name} must be at least {min_value}",
                field=field_name,
                value=value
            )
        
        if max_value is not None and value > max_value:
            raise ValidationException(
                f"{field_name} must not exceed {max_value}",
                field=field_name,
                value=value
            )
    
    @staticmethod
    def validate_float_range(value: Any, field_name: str, min_value: Optional[float] = None, 
                           max_value: Optional[float] = None) -> None:
        """Validate float value and range"""
        if not isinstance(value, (int, float)):
            try:
                value = float(value)
            except (ValueError, TypeError):
                raise ValidationException(
                    f"{field_name} must be a number",
                    field=field_name,
                    value=value
                )
        
        if min_value is not None and value < min_value:
            raise ValidationException(
                f"{field_name} must be at least {min_value}",
                field=field_name,
                value=value
            )
        
        if max_value is not None and value > max_value:
            raise ValidationException(
                f"{field_name} must not exceed {max_value}",
                field=field_name,
                value=value
            )
    
    @staticmethod
    def validate_datetime(value: Any, field_name: str, format_string: str = "%Y-%m-%d %H:%M:%S") -> datetime:
        """Validate and parse datetime string"""
        if isinstance(value, datetime):
            return value
        
        if not isinstance(value, str):
            raise ValidationException(
                f"{field_name} must be a datetime string",
                field=field_name,
                value=value
            )
        
        try:
            return datetime.strptime(value, format_string)
        except ValueError:
            raise ValidationException(
                f"{field_name} must be in format {format_string}",
                field=field_name,
                value=value
            )
    
    @staticmethod
    def sanitize_html(value: str) -> str:
        """Basic HTML sanitization (remove common dangerous tags)"""
        if not isinstance(value, str):
            return value
        
        # Remove script tags and their content
        value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove other potentially dangerous tags
        dangerous_tags = ['script', 'iframe', 'object', 'embed', 'form', 'input', 'button']
        for tag in dangerous_tags:
            value = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', value, flags=re.IGNORECASE | re.DOTALL)
            value = re.sub(f'<{tag}[^>]*/?>', '', value, flags=re.IGNORECASE)
        
        return value
    
    @staticmethod
    def validate_file_upload(file_data: Any, allowed_extensions: List[str], 
                           max_size_mb: int = 10) -> None:
        """Validate file upload parameters"""
        if not hasattr(file_data, 'name') or not hasattr(file_data, 'size'):
            raise ValidationException("Invalid file object")
        
        # Check file extension
        if not any(file_data.name.lower().endswith(f'.{ext.lower()}') for ext in allowed_extensions):
            raise ValidationException(
                f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}",
                field="file",
                context={"allowed_extensions": allowed_extensions}
            )
        
        # Check file size
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_data.size > max_size_bytes:
            raise ValidationException(
                f"File size exceeds {max_size_mb}MB limit",
                field="file",
                context={"max_size_mb": max_size_mb}
            )

# Content-specific validators
class ContentValidator(DataValidator):
    """Validators specific to content management"""
    
    CONTENT_TYPES = ["Movie", "Trailer", "Reel"]
    CONTENT_STATUSES = ["Ready", "Uploaded", "In Progress", "New"]
    PRIORITY_LEVELS = ["High", "Medium", "Low"]
    
    @staticmethod
    def validate_content_item(data: Dict[str, Any]) -> None:
        """Validate content item data"""
        # Required fields
        ContentValidator.validate_required_fields(data, ["name", "content_type", "status", "priority"])
        
        # String validations
        ContentValidator.validate_string_length(data["name"], "name", min_length=1, max_length=100)
        
        # Choice validations
        ContentValidator.validate_choice(data["content_type"], "content_type", ContentValidator.CONTENT_TYPES)
        ContentValidator.validate_choice(data["status"], "status", ContentValidator.CONTENT_STATUSES)
        ContentValidator.validate_choice(data["priority"], "priority", ContentValidator.PRIORITY_LEVELS)
        
        # Optional description
        if "description" in data and data["description"]:
            ContentValidator.validate_string_length(data["description"], "description", max_length=500)
            data["description"] = ContentValidator.sanitize_html(data["description"])
    
    @staticmethod
    def validate_movie_data(data: Dict[str, Any]) -> None:
        """Validate movie-specific data"""
        ContentValidator.validate_required_fields(data, ["title", "genre"])
        
        ContentValidator.validate_string_length(data["title"], "title", min_length=1, max_length=200)
        ContentValidator.validate_string_length(data["genre"], "genre", min_length=1, max_length=50)
        
        if "duration" in data:
            ContentValidator.validate_integer_range(data["duration"], "duration", min_value=1, max_value=1000)
        
        if "release_date" in data:
            ContentValidator.validate_datetime(data["release_date"], "release_date", "%Y-%m-%d")