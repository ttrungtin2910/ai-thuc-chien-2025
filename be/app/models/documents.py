"""
Document Models

Pydantic models for document management requests and responses.
"""

from pydantic import BaseModel
from typing import Optional, List


class DocumentInfo(BaseModel):
    id: str
    filename: str
    file_type: str
    upload_date: str
    size: int
    public_url: Optional[str] = None
    status: Optional[str] = None


class FileUploadResponse(BaseModel):
    task_id: str
    message: str
    filename: str


class BulkUploadResponse(BaseModel):
    task_id: str
    message: str
    total_files: int


class DocumentDeleteResponse(BaseModel):
    message: str
    details: dict
