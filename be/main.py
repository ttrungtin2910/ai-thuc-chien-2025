"""
DVC.AI Backend Entry Point

Entry point for the DVC.AI backend application.
"""

from app.main import combined_asgi_app

# Export the ASGI app for uvicorn
app = combined_asgi_app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)