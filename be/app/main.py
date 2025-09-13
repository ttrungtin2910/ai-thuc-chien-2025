"""
DVC.AI Main Application

FastAPI application entry point with microservice-style architecture.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import Config
from .core.websocket_manager import websocket_manager
from .api import auth, documents, chatbot, rag, websocket, enhanced_chatbot

# Create FastAPI application
app = FastAPI(
    title=Config.APP_NAME,
    version=Config.APP_VERSION,
    description="Document Management System with AI and Vector Database capabilities",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://10.128.0.4:3000", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix=Config.API_V1_PREFIX)
app.include_router(documents.router, prefix=Config.API_V1_PREFIX)
app.include_router(chatbot.router, prefix=Config.API_V1_PREFIX)
app.include_router(enhanced_chatbot.router, prefix=Config.API_V1_PREFIX)
app.include_router(rag.router, prefix=Config.API_V1_PREFIX)
app.include_router(websocket.router, prefix=Config.API_V1_PREFIX)


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": f"{Config.APP_NAME} API is running",
        "version": Config.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": Config.APP_VERSION
    }


# Create combined ASGI app with WebSocket support
import socketio
combined_asgi_app = socketio.ASGIApp(websocket_manager.sio, app)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:combined_asgi_app",
        host="0.0.0.0",
        port=8001,
        reload=Config.DEBUG
    )
