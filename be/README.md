# DVC.AI Backend

## Quick Setup

```bash
# Complete setup (recommended)
python setup.py

# Install dependencies only
python setup.py --deps

# Start services only
python setup.py --start

# Stop all services
python setup.py --stop

# Show service status
python setup.py --status

# Show help
python setup.py --help
```

## Development

```bash
# Start development environment
python scripts/dev.py start

# Load documents to Milvus
python scripts/load_documents_to_milvus.py
```

## Configuration

1. Update `.env` file with your API keys and configuration
2. For Google Cloud: Update `GOOGLE_APPLICATION_CREDENTIALS` path
3. For OpenAI: Set your `OPENAI_API_KEY`

## Services

- **API Server**: http://localhost:8001
- **MongoDB**: localhost:27017
- **Redis**: localhost:6379
- **Milvus**: localhost:19530
- **Mongo Express**: http://localhost:8081 (admin/admin123)
- **Attu (Milvus UI)**: http://localhost:3001

## Structure

```
be/
├── app/                 # Main application code
├── scripts/            # Utility scripts
├── docker/             # Docker configurations
├── setup.py           # Main setup script
├── requirements.txt   # Python dependencies
└── .env              # Environment configuration
```
