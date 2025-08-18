import requests
import streamlit as st
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from config import DashboardConfig, ContentStatus, Priority, ContentType

@dataclass
class DashboardMetrics:
    total_movies: int
    content_items: int
    uploaded: int
    uploaded_weekly_change: int
    pending: int
    upload_rate: float

@dataclass
class ContentItem:
    id: str
    name: str
    content_type: ContentType
    status: ContentStatus
    priority: Priority
    updated: str
    created_at: datetime = None

@dataclass
class StatusDistribution:
    ready: int
    uploaded: int
    in_progress: int
    new: int

@dataclass
class PriorityDistribution:
    high: int
    medium: int
    low: int

class APIService:
    def __init__(self, config: DashboardConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    @st.cache_data(ttl=30)
    def get_dashboard_metrics(_self) -> DashboardMetrics:
        """Fetch dashboard metrics from API"""
        try:
            # Replace with actual API call
            # response = _self.session.get(f"{_self.config.API_BASE_URL}/metrics")
            # response.raise_for_status()
            # data = response.json()
            
            # Mock data for now - replace with API response
            return DashboardMetrics(
                total_movies=127,
                content_items=2847,
                uploaded=1923,
                uploaded_weekly_change=47,
                pending=234,
                upload_rate=67.5
            )
        except Exception as e:
            st.error(f"Error fetching metrics: {str(e)}")
            return DashboardMetrics(0, 0, 0, 0, 0, 0.0)
    
    @st.cache_data(ttl=30)
    def get_status_distribution(_self) -> StatusDistribution:
        """Fetch content status distribution from API"""
        try:
            # Replace with actual API call
            # response = _self.session.get(f"{_self.config.API_BASE_URL}/status-distribution")
            # response.raise_for_status()
            # data = response.json()
            
            return StatusDistribution(
                ready=45,
                uploaded=38,
                in_progress=25,
                new=19
            )
        except Exception as e:
            st.error(f"Error fetching status distribution: {str(e)}")
            return StatusDistribution(0, 0, 0, 0)
    
    @st.cache_data(ttl=30)
    def get_priority_distribution(_self) -> PriorityDistribution:
        """Fetch priority distribution from API"""
        try:
            # Replace with actual API call
            # response = _self.session.get(f"{_self.config.API_BASE_URL}/priority-distribution")
            # response.raise_for_status()
            # data = response.json()
            
            return PriorityDistribution(
                high=42,
                medium=68,
                low=17
            )
        except Exception as e:
            st.error(f"Error fetching priority distribution: {str(e)}")
            return PriorityDistribution(0, 0, 0)
    
    @st.cache_data(ttl=30)
    def get_recent_activity(_self, limit: int = 10) -> List[ContentItem]:
        """Fetch recent activity from API"""
        try:
            # Replace with actual API call
            # response = _self.session.get(f"{_self.config.API_BASE_URL}/recent-activity?limit={limit}")
            # response.raise_for_status()
            # data = response.json()
            
            # Mock data for now
            return [
                ContentItem(
                    id="1",
                    name="12th Fail",
                    content_type=ContentType.REEL,
                    status=ContentStatus.READY,
                    priority=Priority.HIGH,
                    updated="2 hours ago"
                ),
                ContentItem(
                    id="2",
                    name="2 States",
                    content_type=ContentType.TRAILER,
                    status=ContentStatus.UPLOADED,
                    priority=Priority.MEDIUM,
                    updated="4 hours ago"
                ),
                ContentItem(
                    id="3",
                    name="Laal Singh Chaddha",
                    content_type=ContentType.MOVIE,
                    status=ContentStatus.IN_PROGRESS,
                    priority=Priority.MEDIUM,
                    updated="6 hours ago"
                ),
                ContentItem(
                    id="4",
                    name="Unknown Content",
                    content_type=ContentType.REEL,
                    status=ContentStatus.NEW,
                    priority=Priority.LOW,
                    updated="1 day ago"
                )
            ]
        except Exception as e:
            st.error(f"Error fetching recent activity: {str(e)}")
            return []
    
    def refresh_data(self) -> bool:
        """Refresh all cached data"""
        try:
            # Clear Streamlit cache
            st.cache_data.clear()
            return True
        except Exception as e:
            st.error(f"Error refreshing data: {str(e)}")
            return False
    
    def import_data(self, file_data: bytes, file_type: str) -> Dict:
        """Import data via API"""
        try:
            # files = {'file': (f'import.{file_type}', file_data, f'application/{file_type}')}
            # response = self.session.post(f"{self.config.API_BASE_URL}/import", files=files)
            # response.raise_for_status()
            # return response.json()
            
            # Mock response
            return {"status": "success", "message": "Data imported successfully", "imported_count": 25}
        except Exception as e:
            st.error(f"Error importing data: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def add_content(self, content_data: Dict) -> Dict:
        """Add new content via API"""
        try:
            # response = self.session.post(f"{self.config.API_BASE_URL}/content", json=content_data)
            # response.raise_for_status()
            # return response.json()
            
            # Mock response
            return {"status": "success", "message": "Content added successfully", "id": "new_123"}
        except Exception as e:
            st.error(f"Error adding content: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def update_content_status(self, content_id: str, status: ContentStatus) -> Dict:
        """Update content status via API"""
        try:
            # response = self.session.patch(
            #     f"{self.config.API_BASE_URL}/content/{content_id}/status", 
            #     json={"status": status.value}
            # )
            # response.raise_for_status()
            # return response.json()
            
            # Mock response
            return {"status": "success", "message": f"Content {content_id} status updated to {status.value}"}
        except Exception as e:
            st.error(f"Error updating content status: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def delete_content(self, content_id: str) -> Dict:
        """Delete content via API"""
        try:
            # response = self.session.delete(f"{self.config.API_BASE_URL}/content/{content_id}")
            # response.raise_for_status()
            # return response.json()
            
            # Mock response
            return {"status": "success", "message": f"Content {content_id} deleted successfully"}
        except Exception as e:
            st.error(f"Error deleting content: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def create_movie(self, movie_data: Dict) -> Dict:
        """Create new movie via API"""
        try:
            response = self.session.post(f"{self.config.api.base_url}/movies", json=movie_data)
            response.raise_for_status()
            api_response = response.json()
            
            if api_response.get("success"):
                return {
                    "status": "success", 
                    "message": api_response.get("message", "Movie created successfully"),
                    "data": api_response.get("data", {})
                }
            else:
                return {
                    "status": "error", 
                    "message": api_response.get("message", "Failed to create movie")
                }
        except Exception as e:
            st.error(f"Error creating movie: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_movies_list(self, page: int = 1, limit: int = 20) -> List[Dict]:
        """Get movies list from API"""
        try:
            response = self.session.get(f"{self.config.api.base_url}/movies?page={page}&limit={limit}")
            response.raise_for_status()
            api_response = response.json()
            
            # Extract the data array from the response
            if api_response.get("success") and "data" in api_response:
                return api_response["data"]
            else:
                st.error(f"API Error: {api_response.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            st.error(f"Error fetching movies: {str(e)}")
            return []
    
    def export_movies(self, format: str = "csv", selected_ids: List[str] = None) -> Dict:
        """Export movies to specified format"""
        try:
            # Start the export process
            response = self.session.get(f"{self.config.api.base_url}/export/{format}")
            response.raise_for_status()
            api_response = response.json()
            
            if api_response.get("success"):
                return {
                    "status": "success",
                    "export_id": api_response.get("export_id"),
                    "message": api_response.get("message", f"Export to {format.upper()} started")
                }
            else:
                return {
                    "status": "error",
                    "message": api_response.get("message", "Export failed")
                }
                
        except Exception as e:
            st.error(f"Error starting export: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def download_export_file(self, export_id: str) -> bytes:
        """Download exported file by export ID"""
        try:
            response = self.session.get(f"{self.config.api.base_url}/download/{export_id}")
            response.raise_for_status()
            return response.content
        except Exception as e:
            st.error(f"Error downloading file: {str(e)}")
            return None
    
    def bulk_import_movies_from_file(self, file_content: bytes, filename: str, operation: str = "upsert") -> Dict:
        """Bulk import movies from uploaded file"""
        try:
            # Prepare the file for upload
            files = {
                'file': (filename, file_content, self._get_content_type(filename))
            }
            
            # Use a fresh requests session for file upload to avoid header conflicts
            import requests
            response = requests.post(
                f"{self.config.api.base_url}/movies/bulk-import/file?operation={operation}",
                files=files
            )
            response.raise_for_status()
            api_response = response.json()
            
            if api_response.get("success"):
                return {
                    "status": "success",
                    "data": api_response.get("data", {}),
                    "message": api_response.get("message", "Bulk import completed successfully")
                }
            else:
                return {
                    "status": "error",
                    "message": api_response.get("message", "Bulk import failed")
                }
                
        except Exception as e:
            st.error(f"Error in bulk import: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def download_movie_template(self, template_type: str = "csv") -> bytes:
        """Download movie bulk import template"""
        try:
            response = self.session.get(f"{self.config.api.base_url}/movies/templates/download/{template_type}")
            response.raise_for_status()
            return response.content
        except Exception as e:
            st.error(f"Error downloading template: {str(e)}")
            return None
    
    def _get_content_type(self, filename: str) -> str:
        """Get content type based on file extension"""
        ext = filename.split('.')[-1].lower() if filename else ""
        content_types = {
            "csv": "text/csv",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xls": "application/vnd.ms-excel",
            "json": "application/json"
        }
        return content_types.get(ext, "application/octet-stream")