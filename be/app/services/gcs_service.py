import os
import uuid
from typing import Optional
from google.cloud import storage
from google.oauth2 import service_account
from ..core.config import Config
import logging

logger = logging.getLogger(__name__)

class GCSService:
    def __init__(self):
        self.bucket_name = Config.GCS_BUCKET_NAME
        self.project_id = Config.PROJECT_ID
        self.credentials_path = Config.GOOGLE_APPLICATION_CREDENTIALS
        self.client = None
        self.bucket = None
        self.enabled = False
        
        # Try to initialize client
        try:
            if self.credentials_path and os.path.exists(self.credentials_path):
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                self.client = storage.Client(credentials=credentials, project=self.project_id)
            elif self.project_id:
                # Fallback to default credentials (for Google Cloud environments)
                self.client = storage.Client(project=self.project_id)
            
            if self.client and self.bucket_name:
                self.bucket = self.client.bucket(self.bucket_name)
                self.enabled = True
                logger.info(f"GCS Service initialized successfully with bucket: {self.bucket_name}")
            else:
                logger.warning("GCS Service: Missing bucket name or project configuration")
                
        except Exception as e:
            logger.error(f"GCS Service initialization failed: {e}")
            logger.info("File upload will use local storage only")
            self.client = None
            self.bucket = None
            self.enabled = False
    
    def upload_file(self, file_path: str, destination_path: Optional[str] = None) -> str:
        """
        Upload file to Google Cloud Storage
        
        Args:
            file_path: Local file path
            destination_path: Destination path in GCS bucket (optional)
            
        Returns:
            Public URL of uploaded file or local path if GCS not available
        """
        if not self.enabled or not self.bucket:
            # Return local file path if GCS not available
            filename = os.path.basename(file_path)
            logger.info(f"GCS not available, keeping file locally: {filename}")
            return f"local://{file_path}"
        
        if not destination_path:
            # Generate unique filename
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            destination_path = f"uploads/{uuid.uuid4().hex}_{filename}"
        
        blob = self.bucket.blob(destination_path)
        
        # Upload file
        blob.upload_from_filename(file_path)
        
        # Return the GCS URL (works with uniform bucket-level access)
        # Note: If bucket has uniform bucket-level access enabled, 
        # public access needs to be configured at bucket level
        return f"gs://{self.bucket_name}/{destination_path}"
    
    def upload_file_from_bytes(self, file_content: bytes, filename: str, content_type: str = None) -> str:
        """
        Upload file from bytes to Google Cloud Storage
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            content_type: MIME type of the file
            
        Returns:
            Public URL of uploaded file or local path if GCS not available
        """
        if not self.enabled or not self.bucket:
            # Save to local file if GCS not available
            import tempfile
            temp_dir = tempfile.gettempdir()
            local_path = os.path.join(temp_dir, filename)
            with open(local_path, 'wb') as f:
                f.write(file_content)
            logger.info(f"GCS not available, saved file locally: {filename}")
            return f"local://{local_path}"
        
        # Generate unique filename
        name, ext = os.path.splitext(filename)
        destination_path = f"uploads/{uuid.uuid4().hex}_{filename}"
        
        blob = self.bucket.blob(destination_path)
        
        if content_type:
            blob.content_type = content_type
        
        # Upload file from bytes
        blob.upload_from_string(file_content)
        
        # Return the GCS URL (works with uniform bucket-level access)
        # Note: If bucket has uniform bucket-level access enabled,
        # public access needs to be configured at bucket level
        return f"gs://{self.bucket_name}/{destination_path}"
    
    def delete_file(self, blob_name: str) -> bool:
        """
        Delete file from Google Cloud Storage
        
        Args:
            blob_name: Name of the blob to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.bucket:
            logger.warning("GCS not available, cannot delete file")
            return False
        
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            return True
        except Exception as e:
            logger.error(f"Error deleting file {blob_name}: {e}")
            return False
    
    def list_files(self, prefix: str = "uploads/") -> list:
        """
        List files in GCS bucket with given prefix
        
        Args:
            prefix: Prefix to filter files
            
        Returns:
            List of blob names
        """
        if not self.enabled or not self.bucket:
            logger.warning("GCS not available, cannot list files")
            return []
        
        blobs = self.bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]

# Global instance
gcs_service = GCSService()
