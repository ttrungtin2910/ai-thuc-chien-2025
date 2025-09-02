from celery import Celery
from ..core.config import Config

# Create Celery app
celery_app = Celery(
    "document_processor",
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
    include=['app.workers.tasks']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_disable_rate_limits=True,
    worker_prefetch_multiplier=1,
    # Fix threading issues on Windows
    worker_pool='threads',  # Use threads pool instead of prefork
    worker_concurrency=2,
)

if __name__ == '__main__':
    celery_app.start()
