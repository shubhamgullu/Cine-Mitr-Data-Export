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
from database.connection import db_manager
from database.repository import AnalyticsRepository, ContentRepository
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
        """Get dashboard metrics from database"""
        cache_key = "dashboard_metrics"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        with db_manager.get_session() as session:
            analytics_repo = AnalyticsRepository(session)
            metrics_data = analytics_repo.get_dashboard_metrics()
            
            metrics = DashboardMetrics(**metrics_data)
        
        self._cache_result(cache_key, metrics)
        return metrics

    async def get_status_distribution(self) -> StatusDistribution:
        """Get content status distribution from database"""
        cache_key = "status_distribution"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        with db_manager.get_session() as session:
            analytics_repo = AnalyticsRepository(session)
            distribution_data = analytics_repo.get_status_distribution()
            
            distribution = StatusDistribution(**distribution_data)
        
        self._cache_result(cache_key, distribution)
        return distribution

    async def get_priority_distribution(self) -> PriorityDistribution:
        """Get priority distribution from database"""
        cache_key = "priority_distribution"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        with db_manager.get_session() as session:
            analytics_repo = AnalyticsRepository(session)
            distribution_data = analytics_repo.get_priority_distribution()
            
            distribution = PriorityDistribution(**distribution_data)
        
        self._cache_result(cache_key, distribution)
        return distribution

    async def get_recent_activity(self, limit: int = 10) -> List[RecentActivity]:
        """Get recent activity from database"""
        cache_key = f"recent_activity_{limit}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        with db_manager.get_session() as session:
            content_repo = ContentRepository(session)
            db_content_list = content_repo.get_recent_activity(limit)
            
            activities = []
            for db_content in db_content_list:
                # Calculate time ago string
                time_diff = datetime.utcnow() - db_content.updated_at
                if time_diff.days > 0:
                    if time_diff.days == 1:
                        updated_str = "1 day ago"
                    elif time_diff.days < 7:
                        updated_str = f"{time_diff.days} days ago"
                    else:
                        updated_str = f"{time_diff.days // 7} week{'s' if time_diff.days // 7 > 1 else ''} ago"
                else:
                    hours = time_diff.seconds // 3600
                    if hours > 0:
                        updated_str = f"{hours} hour{'s' if hours > 1 else ''} ago"
                    else:
                        minutes = time_diff.seconds // 60
                        updated_str = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
                
                activity = RecentActivity(
                    id=db_content.id,
                    name=db_content.name,
                    content_type=ContentType(db_content.content_type),
                    status=ContentStatus(db_content.status),
                    priority=Priority(db_content.priority),
                    updated=updated_str,
                    updated_at=db_content.updated_at,
                    thumbnail_url=db_content.thumbnail_url,
                    file_size_mb=round((db_content.file_size_bytes or 0) / (1024 * 1024), 1),
                    duration_minutes=(db_content.duration_seconds or 0) // 60
                )
                activities.append(activity)
        
        self._cache_result(cache_key, activities)
        return activities

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