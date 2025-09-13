# 🛠️ Development Guide - DVC.AI

## 🚀 **Development Setup**

### **Prerequisites**
- Python 3.8+ (recommended 3.11)
- Node.js 16+ và npm
- Docker & Docker Compose
- Git
- IDE: VS Code (recommended)

### **Quick Development Setup**
```bash
# 1. Clone repository
git clone <repository-url>
cd dvc-ai-project

# 2. Setup backend environment
cd be
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate     # Windows

pip install -r requirements.txt

# 3. Setup frontend environment  
cd ../fe
npm install

# 4. Start development services
cd ../be
python scripts/dev.py start
```

---

## 📁 **Project Structure**

### **Backend Structure**
```
be/
├── main.py                 # Application entry point
├── app/                    # Main application package
│   ├── __init__.py
│   ├── main.py            # FastAPI app configuration
│   ├── api/               # REST API endpoints
│   │   ├── auth.py        # Authentication routes
│   │   ├── documents.py   # Document management
│   │   ├── chatbot.py     # Chatbot interactions
│   │   ├── rag.py         # RAG system routes
│   │   └── websocket.py   # WebSocket endpoints
│   ├── agent/             # LangGraph Agent system
│   │   ├── configuration.py
│   │   ├── graph_builder.py
│   │   ├── state.py
│   │   ├── chains.py
│   │   ├── prompts.py
│   │   └── nodes/         # Agent nodes
│   ├── core/              # Core utilities
│   │   ├── config.py      # Configuration
│   │   ├── security.py    # Authentication
│   │   └── websocket.py   # WebSocket manager
│   ├── models/            # Pydantic models
│   ├── services/          # External services
│   └── utils/             # Utility functions
├── scripts/               # Development scripts
├── data/                  # Data files
└── requirements.txt       # Python dependencies
```

### **Frontend Structure**
```
fe/
├── public/                # Static assets
│   ├── fonts/            # MaisonNeue font files
│   └── index.html
├── src/
│   ├── components/       # React components
│   ├── pages/           # Page components
│   ├── services/        # API services
│   ├── contexts/        # React contexts
│   ├── App.js          # Main app component
│   └── index.js        # Entry point
├── package.json         # Node.js dependencies
└── nginx.conf          # Production nginx config
```

---

## 🔧 **Development Commands**

### **Backend Development**
```bash
cd be

# Start development server (with auto-reload)
python scripts/dev.py start

# Run specific service only
python scripts/dev.py start --service mongodb
python scripts/dev.py start --service milvus  
python scripts/dev.py start --service redis

# Stop all services
python scripts/dev.py stop

# Check service status
python scripts/dev.py status

# Load sample documents
python scripts/load_documents_to_milvus.py

# Run tests
pytest tests/

# Check code style
flake8 app/
black app/ --check

# Format code
black app/
isort app/
```

### **Frontend Development**
```bash
cd fe

# Start development server (hot reload)
npm start

# Build for production
npm run build

# Run tests
npm test

# Check code style
npm run lint

# Fix lint issues
npm run lint:fix
```

### **Docker Development**
```bash
# Build development images
docker-compose -f docker-compose.dev.yml build

# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart specific service
docker-compose restart backend
```

---

## 🧪 **Testing**

### **Backend Testing**
```bash
cd be

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v -s
```

### **Test Structure**
```
be/tests/
├── __init__.py
├── conftest.py            # Test configuration
├── test_auth.py          # Authentication tests
├── test_documents.py     # Document management tests
├── test_chatbot.py       # Chatbot tests
├── test_rag.py           # RAG system tests
└── test_services/        # Service tests
    ├── test_milvus.py
    ├── test_mongodb.py
    └── test_openai.py
```

### **Writing Tests**
```python
# Example test file: tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_success():
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_protected_endpoint():
    # Test với authentication header
    headers = {"Authorization": "Bearer valid_token"}
    response = client.get("/api/protected", headers=headers)
    assert response.status_code == 200
```

---

## 📚 **API Development**

### **Adding New Endpoints**
```python
# 1. Create model (app/models/feature.py)
from pydantic import BaseModel

class FeatureRequest(BaseModel):
    name: str
    description: str

class FeatureResponse(BaseModel):
    id: int
    name: str
    status: str

# 2. Create service (app/services/feature_service.py)
class FeatureService:
    async def create_feature(self, request: FeatureRequest):
        # Business logic here
        return FeatureResponse(id=1, name=request.name, status="created")

# 3. Create API route (app/api/feature.py)
from fastapi import APIRouter, Depends
from app.models.feature import FeatureRequest, FeatureResponse
from app.services.feature_service import FeatureService

router = APIRouter(prefix="/api/features")

@router.post("/", response_model=FeatureResponse)
async def create_feature(
    request: FeatureRequest,
    service: FeatureService = Depends()
):
    return await service.create_feature(request)

# 4. Register router (app/main.py)
from app.api import feature
app.include_router(feature.router)
```

### **API Documentation**
```python
# FastAPI tự động tạo docs tại:
# http://localhost:8001/docs (Swagger UI)
# http://localhost:8001/redoc (ReDoc)

# Custom documentation
@router.post(
    "/",
    response_model=FeatureResponse,
    summary="Create a new feature",
    description="Creates a new feature with the provided information",
    tags=["Features"]
)
async def create_feature(request: FeatureRequest):
    """
    Create a new feature:
    
    - **name**: Feature name (required)
    - **description**: Feature description (optional)
    
    Returns the created feature with generated ID.
    """
    pass
```

---

## 🤖 **Agent Development**

### **Adding New Agent Nodes**
```python
# 1. Create node class (app/agent/nodes/new_node.py)
from typing import Dict, Any
from app.agent.state import ChatState

class NewProcessingNode:
    """Custom processing node for specific functionality"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def process(self, state: ChatState) -> ChatState:
        """Main processing logic"""
        # Your custom logic here
        processed_data = self.custom_processing(state.query)
        
        # Update state
        state.custom_field = processed_data
        return state
    
    def custom_processing(self, query: str) -> str:
        """Implement your custom logic"""
        return f"Processed: {query}"

# 2. Register node (app/agent/graph_builder.py)
from app.agent.nodes.new_node import NewProcessingNode

class GraphBuilder:
    def build_graph(self):
        # Add your node to the graph
        new_node = NewProcessingNode(self.config)
        self.graph.add_node("new_processing", new_node.process)
        
        # Add edges
        self.graph.add_edge("previous_node", "new_processing")
        self.graph.add_edge("new_processing", "next_node")
```

### **Custom Prompts**
```python
# app/agent/prompts.py
CUSTOM_PROMPT = """
You are a helpful assistant for Vietnamese administrative procedures.

Context: {context}
Query: {query}

Please provide a helpful response based on the context.
Include relevant citations where appropriate.

Response:
"""

# Usage in nodes
from app.agent.prompts import CUSTOM_PROMPT

class CustomGeneratorNode:
    async def generate(self, state: ChatState) -> str:
        prompt = CUSTOM_PROMPT.format(
            context=state.documents,
            query=state.query
        )
        response = await self.llm.ainvoke(prompt)
        return response.content
```

---

## 🎨 **Frontend Development**

### **Adding New Components**
```jsx
// src/components/NewComponent.js
import React, { useState, useEffect } from 'react';
import './NewComponent.css';

const NewComponent = ({ prop1, prop2, onAction }) => {
  const [state, setState] = useState(null);

  useEffect(() => {
    // Component initialization
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await fetch('/api/data');
      const data = await response.json();
      setState(data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const handleAction = () => {
    onAction(state);
  };

  return (
    <div className="new-component">
      <h3>New Component</h3>
      {state && (
        <div className="content">
          {/* Component content */}
        </div>
      )}
      <button onClick={handleAction}>Action</button>
    </div>
  );
};

export default NewComponent;
```

### **Styling Guidelines**
```css
/* Use MaisonNeue font family */
.component {
  font-family: 'MaisonNeue', Arial, sans-serif;
}

/* Follow orange-brown color scheme */
:root {
  --primary-orange: #D2691E;
  --secondary-brown: #8B4513;
  --accent-gold: #FFD700;
  --text-dark: #2F2F2F;
  --background-light: #FFF8DC;
}

/* Component-specific styles */
.new-component {
  background: var(--background-light);
  border: 1px solid var(--primary-orange);
  border-radius: 8px;
  padding: 1rem;
}
```

---

## 🔄 **CI/CD Development**

### **Pre-commit Hooks**
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.8

  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```

### **GitHub Actions (Example)**
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    
    - name: Install dependencies
      run: |
        cd be
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        cd be
        pytest --cov=app
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

---

## 🐛 **Debugging**

### **Backend Debugging**
```python
# Enable debug mode
# app/core/config.py
DEBUG = True
LOG_LEVEL = "DEBUG"

# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debugger
import pdb; pdb.set_trace()  # Breakpoint
```

### **VS Code Debug Configuration**
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/be/main.py",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/be"
            }
        }
    ]
}
```

### **Common Debug Commands**
```bash
# Check service logs
docker-compose logs -f backend

# Connect to database
docker-compose exec mongo mongosh -u admin -p dvcai2025

# Check Milvus collection
python scripts/debug_milvus.py

# Test API endpoints
curl -X POST http://localhost:8001/api/test \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

---

## 📦 **Deployment Preparation**

### **Environment Configuration**
```bash
# Create production .env
cp .env.example .env.production

# Required production variables
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=strong-production-secret
OPENAI_API_KEY=real-api-key
```

### **Build Production Images**
```bash
# Build optimized images
docker build -t dvc-ai-backend:prod ./be
docker build -t dvc-ai-frontend:prod ./fe

# Test production build
docker-compose -f docker-compose.prod.yml up -d
```

### **Performance Testing**
```bash
# Load testing với artillery
npm install -g artillery
artillery quick --count 100 --num 10 http://localhost:8001/api/health

# Database performance testing
python scripts/benchmark_database.py
```

---

## 📖 **Best Practices**

### **Code Quality**
- Follow PEP 8 for Python code
- Use type hints consistently
- Write descriptive commit messages
- Keep functions small and focused
- Add docstrings to all functions

### **Security**
- Never commit API keys or secrets
- Use environment variables for configuration
- Validate all user inputs
- Implement proper error handling
- Use HTTPS in production

### **Performance**
- Use async/await for I/O operations
- Implement proper database indexing
- Cache frequently accessed data
- Optimize query performance
- Monitor application metrics

---

*Happy coding! 🚀*
