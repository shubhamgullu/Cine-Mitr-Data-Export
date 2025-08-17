"""
Simple validators stub for testing
"""

from models import FileValidationResult

async def validate_file_upload(file, config):
    """Validate file upload (stub implementation)"""
    return FileValidationResult(
        is_valid=True,
        error_message=None,
        file_size_mb=10.0,
        file_extension=".mp4"
    )