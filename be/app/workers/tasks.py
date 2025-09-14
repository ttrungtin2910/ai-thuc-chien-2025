import os
import asyncio
import threading
from celery import current_task
from .celery_app import celery_app
from ..services.gcs_service import gcs_service
from ..services.milvus_service import MilvusService
from ..services.openai_service import openai_service
from ..utils.document_processor import DocumentProcessor
from ..core.websocket import websocket_manager
from ..core.config import Config
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

from ..services.database import add_document

def send_websocket_message(user_id: str, message: dict):
    """Helper function to send WebSocket message from sync context"""
    try:
        logger.info(f"WebSocket message for user {user_id}: {message['type']}")
        
        def run_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                if message['type'] == 'file_upload_progress':
                    loop.run_until_complete(
                        websocket_manager.sio.emit('file_upload_progress', message)
                    )
                elif message['type'] == 'file_upload_complete':
                    loop.run_until_complete(
                        websocket_manager.sio.emit('file_upload_complete', message)
                    )
                elif message['type'] == 'file_upload_error':
                    loop.run_until_complete(
                        websocket_manager.sio.emit('file_upload_error', message)
                    )
                elif message['type'] == 'bulk_upload_progress':
                    loop.run_until_complete(
                        websocket_manager.sio.emit('bulk_upload_progress', message)
                    )
                elif message['type'] == 'bulk_upload_complete':
                    loop.run_until_complete(
                        websocket_manager.sio.emit('bulk_upload_complete', message)
                    )
                elif message['type'] == 'bulk_upload_error':
                    loop.run_until_complete(
                        websocket_manager.sio.emit('bulk_upload_error', message)
                    )
                elif message['type'] == 'file_processing_update':
                    loop.run_until_complete(
                        websocket_manager.sio.emit('file_processing_update', message)
                    )
                    
                logger.info(f"WebSocket message sent successfully: {message['type']}")
                
            except Exception as e:
                logger.error(f"Error in async WebSocket send: {e}")
            finally:
                try:
                    loop.close()
                except:
                    pass
        
        thread = threading.Thread(target=run_async)
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        logger.error(f"Error sending WebSocket message: {e}")

@celery_app.task(bind=True)
def process_file_upload(self, file_path: str, filename: str, user_id: str, task_id: str):
    """Process file upload with content extraction and Milvus storage"""
    try:
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Starting upload...'}
        )
        
        send_websocket_message(user_id, {
            'type': 'file_upload_progress',
            'task_id': task_id,
            'filename': filename,
            'status': 'uploading',
            'progress': 5
        })
        
        send_websocket_message(user_id, {
            'type': 'file_processing_update',
            'task_id': task_id,
            'filename': filename,
            'status': 'uploading',
            'progress': 5
        })
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Step 1: Extract content using Document Processor
        logger.info(f"🎬 [UPLOAD-TASK] Starting file processing for: {filename}")
        logger.info(f"📍 [UPLOAD-TASK] Task ID: {task_id}, User: {user_id}")
        logger.info(f"📁 [UPLOAD-TASK] File path: {file_path}")
        
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 15, 'total': 100, 'status': 'Extracting content from file...'}
        )
        
        send_websocket_message(user_id, {
            'type': 'file_processing_update',
            'task_id': task_id,
            'filename': filename,
            'status': 'extracting_content',
            'progress': 15
        })
        
        # Initialize document processor with OpenAI service
        logger.info(f"🔧 [UPLOAD-TASK] Initializing document processor with OpenAI service")
        doc_processor = DocumentProcessor(openai_service=openai_service)
        
        # Step 2: Upload to Google Cloud Storage
        logger.info(f"☁️ [UPLOAD-TASK] Step 2: Uploading to Google Cloud Storage")
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 35, 'total': 100, 'status': 'Uploading to Google Cloud Storage...'}
        )
        
        send_websocket_message(user_id, {
            'type': 'file_processing_update',
            'task_id': task_id,
            'filename': filename,
            'status': 'uploading_to_cloud',
            'progress': 35
        })
        
        public_url = gcs_service.upload_file(file_path, f"documents/{filename}")
        logger.info(f"✅ [UPLOAD-TASK] File uploaded to GCS: {public_url}")
        
        # Step 3: Process and save to Milvus
        logger.info(f"🗄️ [UPLOAD-TASK] Step 3: Processing and saving to Milvus vector database")
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 60, 'total': 100, 'status': 'Processing content and saving to vector database...'}
        )
        
        send_websocket_message(user_id, {
            'type': 'file_processing_update',
            'task_id': task_id,
            'filename': filename,
            'status': 'saving_to_vector_db',
            'progress': 60
        })
        
        # Initialize and connect to Milvus
        logger.info(f"🔌 [UPLOAD-TASK] Connecting to Milvus at {Config.MILVUS_HOST}:{Config.MILVUS_PORT}")
        milvus_service = MilvusService(host=Config.MILVUS_HOST, port=Config.MILVUS_PORT)
        
        if milvus_service.connect():
            logger.info(f"✅ [UPLOAD-TASK] Connected to Milvus successfully")
            
            logger.info(f"🏗️ [UPLOAD-TASK] Setting up Milvus collection")
            milvus_service.create_collection()
            milvus_service.load_collection()
            
            # Process and save to Milvus
            logger.info(f"💾 [UPLOAD-TASK] Processing and saving file to Milvus")
            milvus_success = doc_processor.process_and_save_to_milvus(
                file_path, filename, milvus_service
            )
            
            if milvus_success:
                logger.info(f"🎉 [UPLOAD-TASK] Successfully saved {filename} to Milvus")
            else:
                logger.error(f"❌ [UPLOAD-TASK] Failed to save {filename} to Milvus, but continuing with upload")
            
            milvus_service.disconnect()
            logger.info(f"🔌 [UPLOAD-TASK] Disconnected from Milvus")
        else:
            logger.error(f"❌ [UPLOAD-TASK] Failed to connect to Milvus, skipping vector database storage")
            logger.error(f"🔧 [UPLOAD-TASK] Check if Milvus is running at {Config.MILVUS_HOST}:{Config.MILVUS_PORT}")
        
        # Step 4: Save document metadata
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 85, 'total': 100, 'status': 'Finalizing...'}
        )
        
        send_websocket_message(user_id, {
            'type': 'file_processing_update',
            'task_id': task_id,
            'filename': filename,
            'status': 'finalizing',
            'progress': 85
        })
        
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        file_extension = os.path.splitext(filename)[1].lower()
        
        document = add_document(
            filename=filename,
            file_type=file_extension,
            size=file_size,
            public_url=public_url,
            stored_filename=filename
        )
        
        # Clean up temporary file
        try:
            os.remove(file_path)
        except Exception as e:
            logger.warning(f"Could not remove local file {file_path}: {e}")
        
        # Completion
        send_websocket_message(user_id, {
            'type': 'file_upload_complete',
            'task_id': task_id,
            'filename': filename,
            'status': 'completed',
            'public_url': public_url,
            'progress': 100,
            'document_id': document['id']
        })
        
        return {
            'status': 'completed',
            'filename': filename,
            'public_url': public_url,
            'document_id': document['id'],
            'message': f'File {filename} uploaded and processed successfully'
        }
        
    except Exception as e:
        send_websocket_message(user_id, {
            'type': 'file_upload_error',
            'task_id': task_id,
            'filename': filename,
            'status': 'failed',
            'error': str(e)
        })
        
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
    """Process bulk file upload"""
    try:
        total_files = len(file_paths)
        completed_files = 0
        failed_files = []
        successful_uploads = []
        
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
                send_websocket_message(user_id, {
                    'type': 'file_processing_update',
                    'task_id': f"{bulk_task_id}_{filename}",
                    'filename': filename,
                    'status': 'extracting_content',
                    'progress': 10
                })
                
                # Initialize document processor for bulk processing
                doc_processor = DocumentProcessor(openai_service=openai_service)
                
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                file_extension = os.path.splitext(filename)[1].lower()
                
                send_websocket_message(user_id, {
                    'type': 'file_processing_update',
                    'task_id': f"{bulk_task_id}_{filename}",
                    'filename': filename,
                    'status': 'uploading_to_cloud',
                    'progress': 35
                })
                
                public_url = gcs_service.upload_file(file_path, f"documents/{filename}")
                
                send_websocket_message(user_id, {
                    'type': 'file_processing_update',
                    'task_id': f"{bulk_task_id}_{filename}",
                    'filename': filename,
                    'status': 'saving_to_vector_db',
                    'progress': 65
                })
                
                # Process and save to Milvus
                milvus_service = MilvusService(host=Config.MILVUS_HOST, port=Config.MILVUS_PORT)
                if milvus_service.connect():
                    milvus_service.create_collection()
                    milvus_service.load_collection()
                    
                    milvus_success = doc_processor.process_and_save_to_milvus(
                        file_path, filename, milvus_service
                    )
                    
                    if not milvus_success:
                        logger.warning(f"Failed to save {filename} to Milvus during bulk upload")
                    
                    milvus_service.disconnect()
                
                document = add_document(
                    filename=filename,
                    file_type=file_extension,
                    size=file_size,
                    public_url=public_url,
                    stored_filename=filename
                )
                
                successful_uploads.append({
                    'filename': filename,
                    'public_url': public_url,
                    'document_id': document['id']
                })
                
                send_websocket_message(user_id, {
                    'type': 'file_processing_update',
                    'task_id': f"{bulk_task_id}_{filename}",
                    'filename': filename,
                    'status': 'completed',
                    'progress': 100
                })
                
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.warning(f"Could not remove local file {file_path}: {e}")
                    
            except Exception as e:
                failed_files.append({
                    'filename': filename,
                    'error': str(e)
                })
            
            completed_files += 1
            progress = (completed_files / total_files) * 100
            
            send_websocket_message(user_id, {
                'type': 'bulk_upload_progress',
                'bulk_task_id': bulk_task_id,
                'total_files': total_files,
                'completed_files': completed_files,
                'progress': progress,
                'status': 'processing'
            })
        
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
