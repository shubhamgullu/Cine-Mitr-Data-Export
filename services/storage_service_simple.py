"""
Simple storage service stub for testing
"""

import asyncio
import uuid
from datetime import datetime
from models import StorageStats
from utils.logger import setup_logger

logger = setup_logger(__name__)

class StorageService:
    def __init__(self):
        pass

    async def get_storage_stats(self):
        """Get storage statistics (stub implementation)"""
        return StorageStats(
            total_size_gb=1000.0,
            used_size_gb=680.0,
            available_size_gb=320.0,
            usage_percentage=68.0,
            file_count=150,
            largest_files=[]
        )

    async def start_cleanup(self, cleanup_request):
        """Start cleanup process (stub implementation)"""
        return str(uuid.uuid4())

    async def perform_cleanup(self, cleanup_id: str):
        """Perform cleanup (stub implementation)"""
        pass

    async def get_file_path(self, file_id: str):
        """Get file path (stub implementation)"""
        return None