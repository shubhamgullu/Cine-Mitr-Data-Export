"""
Upload service for handling file uploads and processing
"""

import asyncio
import uuid
import os
import shutil
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
from fastapi import UploadFile
from models import (
    UploadResult, UploadStatusInfo, UploadStatus, 
    ContentType, Priority
)
from utils.logger import setup_logger
from config import DashboardConfig

logger = setup_logger(__name__)

class UploadService:
    def __init__(self):
        self.config = DashboardConfig()
        self.upload_storage = {}  # In-memory storage for upload status
        self.bulk_uploads = {}    # Track bulk upload progress
        
        # Ensure upload directory exists
        self.upload_dir = Path(self.config.file_upload.upload_folder)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        """Initialize the upload service"""
        logger.info("Initializing Upload Service")
        
        # Clean up any temporary files from previous runs
        await self._cleanup_temp_files()

    async def upload_file(
        self, 
        file: UploadFile, 
        content_type: str, 
        priority: str
    ) -> UploadResult:
        """Upload a single file"""
        upload_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        # Create upload status
        status_info = UploadStatusInfo(
            upload_id=upload_id,
            status=UploadStatus.UPLOADING,
            progress_percentage=0.0,
            file_name=file.filename,
            file_size_bytes=0,  # Will be updated during upload
            bytes_uploaded=0,
            started_at=timestamp
        )
        
        self.upload_storage[upload_id] = status_info
        
        try:
            # Read file content
            content = await file.read()
            file_size = len(content)
            
            # Update file size
            status_info.file_size_bytes = file_size
            status_info.bytes_uploaded = file_size
            status_info.progress_percentage = 100.0
            
            # Save file to disk
            file_path = self.upload_dir / f"{upload_id}_{file.filename}"
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Update status to processing
            status_info.status = UploadStatus.PROCESSING
            
            # Simulate processing time
            await asyncio.sleep(1)
            
            # Complete upload
            status_info.status = UploadStatus.COMPLETED
            status_info.completed_at = datetime.utcnow()
            
            result = UploadResult(
                upload_id=upload_id,
                file_name=file.filename,
                file_size_bytes=file_size,
                content_type=content_type,
                status=UploadStatus.COMPLETED,
                created_at=timestamp
            )
            
            logger.info(f"File uploaded successfully: {file.filename} ({upload_id})")
            return result
            
        except Exception as e:
            # Mark upload as failed
            status_info.status = UploadStatus.FAILED
            status_info.error_message = str(e)
            status_info.completed_at = datetime.utcnow()
            
            logger.error(f"Upload failed for {file.filename}: {str(e)}")
            raise

    async def start_bulk_upload(
        self, 
        files: List[UploadFile], 
        content_type: str, 
        priority: str
    ) -> str:
        """Start bulk upload process"""
        bulk_upload_id = str(uuid.uuid4())
        
        # Initialize bulk upload tracking
        self.bulk_uploads[bulk_upload_id] = {
            "status": UploadStatus.PENDING,
            "total_files": len(files),
            "completed_files": 0,
            "failed_files": 0,
            "files": [],
            "started_at": datetime.utcnow(),
            "content_type": content_type,
            "priority": priority
        }
        
        # Store file information for processing
        for file in files:
            file_info = {
                "filename": file.filename,
                "size": 0,  # Will be updated during processing
                "upload_id": str(uuid.uuid4()),
                "status": UploadStatus.PENDING
            }
            self.bulk_uploads[bulk_upload_id]["files"].append(file_info)
        
        logger.info(f"Started bulk upload {bulk_upload_id} for {len(files)} files")
        return bulk_upload_id

    async def process_bulk_upload(self, bulk_upload_id: str):
        """Process bulk upload in background"""
        if bulk_upload_id not in self.bulk_uploads:
            logger.error(f"Bulk upload {bulk_upload_id} not found")
            return
        
        bulk_info = self.bulk_uploads[bulk_upload_id]
        bulk_info["status"] = UploadStatus.UPLOADING
        
        logger.info(f"Processing bulk upload {bulk_upload_id}")
        
        try:
            for i, file_info in enumerate(bulk_info["files"]):
                try:
                    # Simulate file processing
                    await asyncio.sleep(0.5)  # Simulate upload time
                    
                    file_info["status"] = UploadStatus.COMPLETED
                    file_info["size"] = 1024 * 1024 * (10 + i)  # Mock file sizes
                    bulk_info["completed_files"] += 1
                    
                    logger.info(f"Processed file {i+1}/{bulk_info['total_files']}: {file_info['filename']}")
                    
                except Exception as e:
                    file_info["status"] = UploadStatus.FAILED
                    file_info["error"] = str(e)
                    bulk_info["failed_files"] += 1
                    logger.error(f"Failed to process file {file_info['filename']}: {str(e)}")
            
            # Mark bulk upload as completed
            bulk_info["status"] = UploadStatus.COMPLETED
            bulk_info["completed_at"] = datetime.utcnow()
            
            logger.info(f"Bulk upload {bulk_upload_id} completed: "
                       f"{bulk_info['completed_files']} successful, "
                       f"{bulk_info['failed_files']} failed")
        
        except Exception as e:
            bulk_info["status"] = UploadStatus.FAILED
            bulk_info["error"] = str(e)
            bulk_info["completed_at"] = datetime.utcnow()
            logger.error(f"Bulk upload {bulk_upload_id} failed: {str(e)}")

    async def get_upload_status(self, upload_id: str) -> Optional[UploadStatusInfo]:
        """Get upload status for single file upload"""
        return self.upload_storage.get(upload_id)

    async def get_bulk_upload_status(self, bulk_upload_id: str) -> Optional[Dict[str, Any]]:
        """Get bulk upload status"""
        if bulk_upload_id not in self.bulk_uploads:
            return None
        
        bulk_info = self.bulk_uploads[bulk_upload_id].copy()
        
        # Calculate overall progress
        if bulk_info["total_files"] > 0:
            completed = bulk_info["completed_files"] + bulk_info["failed_files"]
            bulk_info["progress_percentage"] = (completed / bulk_info["total_files"]) * 100
        else:
            bulk_info["progress_percentage"] = 0
        
        return bulk_info

    async def cleanup_old_uploads(self, days_old: int = 7):
        """Cleanup old upload files and records"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Clean up file records
        to_remove = []
        for upload_id, status_info in self.upload_storage.items():
            if status_info.started_at < cutoff_date:
                to_remove.append(upload_id)
        
        for upload_id in to_remove:
            del self.upload_storage[upload_id]
        
        # Clean up bulk upload records
        to_remove_bulk = []
        for bulk_id, bulk_info in self.bulk_uploads.items():
            if bulk_info["started_at"] < cutoff_date:
                to_remove_bulk.append(bulk_id)
        
        for bulk_id in to_remove_bulk:
            del self.bulk_uploads[bulk_id]
        
        # Clean up actual files
        await self._cleanup_old_files(days_old)
        
        logger.info(f"Cleaned up {len(to_remove)} uploads and {len(to_remove_bulk)} bulk uploads")

    async def _cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            if self.upload_dir.exists():
                temp_files = list(self.upload_dir.glob("temp_*"))
                for temp_file in temp_files:
                    temp_file.unlink()
                logger.info(f"Cleaned up {len(temp_files)} temporary files")
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {str(e)}")

    async def _cleanup_old_files(self, days_old: int):
        """Clean up old uploaded files"""
        try:
            cutoff_timestamp = datetime.utcnow().timestamp() - (days_old * 24 * 3600)
            
            if not self.upload_dir.exists():
                return
            
            removed_count = 0
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file():
                    file_stat = file_path.stat()
                    if file_stat.st_mtime < cutoff_timestamp:
                        file_path.unlink()
                        removed_count += 1
            
            logger.info(f"Cleaned up {removed_count} old files")
            
        except Exception as e:
            logger.error(f"Error cleaning up old files: {str(e)}")

    async def get_upload_stats(self) -> Dict[str, Any]:
        """Get upload statistics"""
        total_uploads = len(self.upload_storage)
        completed_uploads = sum(1 for status in self.upload_storage.values() 
                               if status.status == UploadStatus.COMPLETED)
        failed_uploads = sum(1 for status in self.upload_storage.values() 
                            if status.status == UploadStatus.FAILED)
        active_uploads = sum(1 for status in self.upload_storage.values() 
                            if status.status in [UploadStatus.UPLOADING, UploadStatus.PROCESSING])
        
        total_bulk_uploads = len(self.bulk_uploads)
        completed_bulk = sum(1 for bulk in self.bulk_uploads.values() 
                            if bulk["status"] == UploadStatus.COMPLETED)
        
        return {
            "total_uploads": total_uploads,
            "completed_uploads": completed_uploads,
            "failed_uploads": failed_uploads,
            "active_uploads": active_uploads,
            "total_bulk_uploads": total_bulk_uploads,
            "completed_bulk_uploads": completed_bulk,
            "upload_directory_size_mb": await self._get_directory_size()
        }

    async def _get_directory_size(self) -> float:
        """Get total size of upload directory in MB"""
        try:
            total_size = 0
            if self.upload_dir.exists():
                for file_path in self.upload_dir.rglob("*"):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
            return total_size / (1024 * 1024)  # Convert to MB
        except Exception as e:
            logger.error(f"Error calculating directory size: {str(e)}")
            return 0.0