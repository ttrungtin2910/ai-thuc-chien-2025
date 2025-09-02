import os
import asyncio
import threading
from celery import current_task
from celery_app import celery_app
from services.gcs_service import gcs_service
from websocket_manager import websocket_manager

def send_websocket_message(user_id: str, message: dict):
    """
    Helper function to send WebSocket message from sync context
    """
    try:
        # Use a simple approach - just print for now and avoid complex threading
        print(f"WebSocket message for user {user_id}: {message}")
        # TODO: Implement proper async WebSocket sending later
        # For now, just skip to avoid blocking Celery tasks
        pass
    except Exception as e:
        print(f"Error sending WebSocket message: {e}")
        # Don't raise exception to avoid breaking the task

@celery_app.task(bind=True)
def process_file_upload(self, file_path: str, filename: str, user_id: str, task_id: str):
    """
    Process file upload to Google Cloud Storage
    
    Args:
        file_path: Local file path
        filename: Original filename
        user_id: User ID who uploaded the file
        task_id: Unique task ID for WebSocket communication
    """
    try:
        # Update task status
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Starting upload...'}
        )
        
        # Send WebSocket update
        send_websocket_message(user_id, {
            'type': 'file_upload_progress',
            'task_id': task_id,
            'filename': filename,
            'status': 'uploading',
            'progress': 10
        })
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Update progress
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 25, 'total': 100, 'status': 'Uploading to Google Cloud Storage...'}
        )
        
        # Upload to Google Cloud Storage
        public_url = gcs_service.upload_file(file_path, f"documents/{filename}")
        
        # Update progress
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 75, 'total': 100, 'status': 'Finalizing...'}
        )
        
        # Clean up local file
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not remove local file {file_path}: {e}")
        
        # Send success notification via WebSocket
        send_websocket_message(user_id, {
            'type': 'file_upload_complete',
            'task_id': task_id,
            'filename': filename,
            'status': 'completed',
            'public_url': public_url,
            'progress': 100
        })
        
        return {
            'status': 'completed',
            'filename': filename,
            'public_url': public_url,
            'message': f'File {filename} uploaded successfully'
        }
        
    except Exception as e:
        # Send error notification via WebSocket
        send_websocket_message(user_id, {
            'type': 'file_upload_error',
            'task_id': task_id,
            'filename': filename,
            'status': 'failed',
            'error': str(e)
        })
        
        # Clean up local file on error
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass
        
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(e), 'filename': filename}
        )
        
        raise

@celery_app.task(bind=True)
def process_bulk_upload(self, file_paths: list, user_id: str, bulk_task_id: str):
    """
    Process bulk file upload
    
    Args:
        file_paths: List of file paths with metadata
        user_id: User ID who uploaded the files
        bulk_task_id: Unique bulk task ID
    """
    try:
        total_files = len(file_paths)
        completed_files = 0
        failed_files = []
        successful_uploads = []
        
        # Send initial progress
        send_websocket_message(user_id, {
            'type': 'bulk_upload_progress',
            'bulk_task_id': bulk_task_id,
            'total_files': total_files,
            'completed_files': 0,
            'status': 'starting'
        })
        
        for file_info in file_paths:
            file_path = file_info['path']
            filename = file_info['filename']
            
            try:
                # Upload individual file
                public_url = gcs_service.upload_file(file_path, f"documents/{filename}")
                successful_uploads.append({
                    'filename': filename,
                    'public_url': public_url
                })
                
                # Clean up local file
                try:
                    os.remove(file_path)
                except Exception:
                    pass
                    
            except Exception as e:
                failed_files.append({
                    'filename': filename,
                    'error': str(e)
                })
            
            completed_files += 1
            progress = (completed_files / total_files) * 100
            
            # Send progress update
            send_websocket_message(user_id, {
                'type': 'bulk_upload_progress',
                'bulk_task_id': bulk_task_id,
                'total_files': total_files,
                'completed_files': completed_files,
                'progress': progress,
                'status': 'processing'
            })
        
        # Send completion notification
        send_websocket_message(user_id, {
            'type': 'bulk_upload_complete',
            'bulk_task_id': bulk_task_id,
            'total_files': total_files,
            'successful_uploads': successful_uploads,
            'failed_files': failed_files,
            'status': 'completed'
        })
        
        return {
            'status': 'completed',
            'total_files': total_files,
            'successful_uploads': successful_uploads,
            'failed_files': failed_files
        }
        
    except Exception as e:
        # Send error notification
        send_websocket_message(user_id, {
            'type': 'bulk_upload_error',
            'bulk_task_id': bulk_task_id,
            'error': str(e),
            'status': 'failed'
        })
        
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        raise
