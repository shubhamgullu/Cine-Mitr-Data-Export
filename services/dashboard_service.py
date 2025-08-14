"""
Dashboard service for handling dashboard-related operations
"""

import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta
from models import (
    DashboardMetrics, StatusDistribution, PriorityDistribution, 
    RecentActivity, ContentStatus, Priority, ContentType
)
from utils.logger import setup_logger

logger = setup_logger(__name__)

class DashboardService:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_cache_update = {}

    async def initialize(self):
        """Initialize the dashboard service"""
        logger.info("Initializing Dashboard Service")
        await self._populate_initial_cache()

    async def _populate_initial_cache(self):
        """Populate initial cache with sample data"""
        # In a real implementation, this would fetch from database
        await asyncio.sleep(0.1)  # Simulate async operation

    async def get_metrics(self) -> DashboardMetrics:
        """Get dashboard metrics with enhanced real-time data"""
        cache_key = "dashboard_metrics"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # Simulate database queries
        await asyncio.sleep(0.1)
        
        # Enhanced metrics based on the UI
        metrics = DashboardMetrics(
            total_movies=127,
            content_items=2847,
            uploaded=1923,
            uploaded_weekly_change=47,  # +47 this week
            pending=234,
            upload_rate=67.5,
            storage_used_gb=680.0,
            storage_total_gb=1000.0,  # 1TB total
            active_uploads=12,
            failed_uploads=8
        )
        
        self._cache_result(cache_key, metrics)
        return metrics

    async def get_status_distribution(self) -> StatusDistribution:
        """Get content status distribution for interactive pie chart"""
        cache_key = "status_distribution"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        await asyncio.sleep(0.1)
        
        distribution = StatusDistribution(
            ready=487,      # Ready for upload
            uploaded=856,   # Successfully uploaded
            in_progress=342, # Currently processing
            new=289,        # New items
            failed=45,      # Failed uploads
            processing=78   # Currently processing
        )
        
        self._cache_result(cache_key, distribution)
        return distribution

    async def get_priority_distribution(self) -> PriorityDistribution:
        """Get priority distribution for bar chart"""
        cache_key = "priority_distribution"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        await asyncio.sleep(0.1)
        
        distribution = PriorityDistribution(
            high=342,    # High priority items
            medium=1456, # Medium priority items
            low=1049     # Low priority items
        )
        
        self._cache_result(cache_key, distribution)
        return distribution

    async def get_recent_activity(self, limit: int = 10) -> List[RecentActivity]:
        """Get recent activity with enhanced metadata"""
        cache_key = f"recent_activity_{limit}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        await asyncio.sleep(0.1)
        
        # Enhanced recent activity data matching the UI
        activities = [
            RecentActivity(
                id="content_001",
                name="12th Fail",
                content_type=ContentType.MOVIE,
                status=ContentStatus.READY,
                priority=Priority.HIGH,
                updated="2 hours ago",
                updated_at=datetime.utcnow() - timedelta(hours=2),
                thumbnail_url="/thumbnails/12th_fail.jpg",
                file_size_mb=2456.7,
                duration_minutes=147
            ),
            RecentActivity(
                id="content_002",
                name="2 States",
                content_type=ContentType.TRAILER,
                status=ContentStatus.UPLOADED,
                priority=Priority.MEDIUM,
                updated="4 hours ago",
                updated_at=datetime.utcnow() - timedelta(hours=4),
                thumbnail_url="/thumbnails/2_states.jpg",
                file_size_mb=156.2,
                duration_minutes=3
            ),
            RecentActivity(
                id="content_003",
                name="Laal Singh Chaddha",
                content_type=ContentType.MOVIE,
                status=ContentStatus.IN_PROGRESS,
                priority=Priority.MEDIUM,
                updated="6 hours ago",
                updated_at=datetime.utcnow() - timedelta(hours=6),
                thumbnail_url="/thumbnails/laal_singh.jpg",
                file_size_mb=3245.8,
                duration_minutes=159
            ),
            RecentActivity(
                id="content_004",
                name="Mumbai Meri Jaan - Reel",
                content_type=ContentType.REEL,
                status=ContentStatus.NEW,
                priority=Priority.LOW,
                updated="1 day ago",
                updated_at=datetime.utcnow() - timedelta(days=1),
                thumbnail_url="/thumbnails/mumbai_reel.jpg",
                file_size_mb=45.3,
                duration_minutes=1
            ),
            RecentActivity(
                id="content_005",
                name="Pathaan",
                content_type=ContentType.MOVIE,
                status=ContentStatus.UPLOADED,
                priority=Priority.HIGH,
                updated="1 day ago",
                updated_at=datetime.utcnow() - timedelta(days=1),
                thumbnail_url="/thumbnails/pathaan.jpg",
                file_size_mb=4567.2,
                duration_minutes=146
            ),
            RecentActivity(
                id="content_006",
                name="RRR - Behind Scenes",
                content_type=ContentType.TRAILER,
                status=ContentStatus.PROCESSING,
                priority=Priority.MEDIUM,
                updated="2 days ago",
                updated_at=datetime.utcnow() - timedelta(days=2),
                thumbnail_url="/thumbnails/rrr_bts.jpg",
                file_size_mb=234.5,
                duration_minutes=8
            ),
            RecentActivity(
                id="content_007",
                name="Jawan",
                content_type=ContentType.MOVIE,
                status=ContentStatus.FAILED,
                priority=Priority.HIGH,
                updated="3 days ago",
                updated_at=datetime.utcnow() - timedelta(days=3),
                thumbnail_url="/thumbnails/jawan.jpg",
                file_size_mb=3890.1,
                duration_minutes=169
            ),
            RecentActivity(
                id="content_008",
                name="Kantara Highlights",
                content_type=ContentType.REEL,
                status=ContentStatus.READY,
                priority=Priority.MEDIUM,
                updated="4 days ago",
                updated_at=datetime.utcnow() - timedelta(days=4),
                thumbnail_url="/thumbnails/kantara_reel.jpg",
                file_size_mb=78.9,
                duration_minutes=2
            ),
            RecentActivity(
                id="content_009",
                name="Brahmastra",
                content_type=ContentType.MOVIE,
                status=ContentStatus.UPLOADED,
                priority=Priority.MEDIUM,
                updated="5 days ago",
                updated_at=datetime.utcnow() - timedelta(days=5),
                thumbnail_url="/thumbnails/brahmastra.jpg",
                file_size_mb=4123.7,
                duration_minutes=167
            ),
            RecentActivity(
                id="content_010",
                name="Dangal - Training Scene",
                content_type=ContentType.REEL,
                status=ContentStatus.IN_PROGRESS,
                priority=Priority.LOW,
                updated="1 week ago",
                updated_at=datetime.utcnow() - timedelta(weeks=1),
                thumbnail_url="/thumbnails/dangal_scene.jpg",
                file_size_mb=123.4,
                duration_minutes=4
            )
        ]
        
        # Return only the requested number of items
        result = activities[:limit]
        self._cache_result(cache_key, result)
        return result

    async def refresh_cache(self):
        """Refresh all cached data"""
        logger.info("Refreshing dashboard cache")
        self.cache.clear()
        self.last_cache_update.clear()
        await self._populate_initial_cache()

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in self.cache:
            return False
        
        if cache_key not in self.last_cache_update:
            return False
        
        elapsed = (datetime.utcnow() - self.last_cache_update[cache_key]).total_seconds()
        return elapsed < self.cache_ttl

    def _cache_result(self, cache_key: str, result: Any):
        """Cache a result with timestamp"""
        self.cache[cache_key] = result
        self.last_cache_update[cache_key] = datetime.utcnow()