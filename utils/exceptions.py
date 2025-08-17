"""
Custom exceptions for CineMitr Dashboard
Provides specific exception types for different error scenarios
"""

from typing import Optional, Dict, Any

class CineMitrException(Exception):
    """Base exception class for CineMitr Dashboard"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "context": self.context
        }

class APIException(CineMitrException):
    """Exception raised for API-related errors"""
    
    def __init__(self, message: str, status_code: int = 500, 
                 endpoint: Optional[str] = None, **kwargs):
        self.status_code = status_code
        self.endpoint = endpoint
        context = kwargs.get('context', {})
        context.update({
            "status_code": status_code,
            "endpoint": endpoint
        })
        super().__init__(message, context=context, **kwargs)

class ValidationException(CineMitrException):
    """Exception raised for data validation errors"""
    
    def __init__(self, message: str, field: Optional[str] = None, 
                 value: Optional[Any] = None, **kwargs):
        self.field = field
        self.value = value
        context = kwargs.get('context', {})
        context.update({
            "field": field,
            "invalid_value": str(value) if value is not None else None
        })
        super().__init__(message, error_code="VALIDATION_ERROR", context=context)

class ConfigurationException(CineMitrException):
    """Exception raised for configuration-related errors"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        self.config_key = config_key
        context = kwargs.get('context', {})
        context.update({"config_key": config_key})
        super().__init__(message, error_code="CONFIG_ERROR", context=context)

class AuthenticationException(CineMitrException):
    """Exception raised for authentication errors"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, error_code="AUTH_ERROR", **kwargs)

class AuthorizationException(CineMitrException):
    """Exception raised for authorization errors"""
    
    def __init__(self, message: str = "Access denied", resource: Optional[str] = None, **kwargs):
        self.resource = resource
        context = kwargs.get('context', {})
        context.update({"resource": resource})
        super().__init__(message, error_code="AUTHZ_ERROR", context=context)

class DataNotFoundException(CineMitrException):
    """Exception raised when requested data is not found"""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, 
                 resource_id: Optional[str] = None, **kwargs):
        self.resource_type = resource_type
        self.resource_id = resource_id
        context = kwargs.get('context', {})
        context.update({
            "resource_type": resource_type,
            "resource_id": resource_id
        })
        super().__init__(message, error_code="NOT_FOUND", context=context)

class RateLimitException(CineMitrException):
    """Exception raised when API rate limits are exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", 
                 retry_after: Optional[int] = None, **kwargs):
        self.retry_after = retry_after
        context = kwargs.get('context', {})
        context.update({"retry_after": retry_after})
        super().__init__(message, error_code="RATE_LIMIT", context=context)

class ServiceUnavailableException(CineMitrException):
    """Exception raised when external services are unavailable"""
    
    def __init__(self, message: str, service_name: Optional[str] = None, **kwargs):
        self.service_name = service_name
        context = kwargs.get('context', {})
        context.update({"service": service_name})
        super().__init__(message, error_code="SERVICE_UNAVAILABLE", context=context)

# Alias for backward compatibility
APIError = APIException