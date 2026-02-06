"""
Assignment Platform - FastAPI Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from config import get_settings
from routers import auth, assignments, submissions, reviews, files

settings = get_settings()

# Create uploads directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for Assignment Submission & Review Platform",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to Streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(assignments.router)
app.include_router(submissions.router)
app.include_router(reviews.router)
app.include_router(files.router)

import traceback
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

# Configure logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("backend.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"🔥 GLOBAL EXCEPTION: {exc}")
    logger.error(traceback.format_exc())
    print(f"🔥 GLOBAL EXCEPTION: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
    )

async def root():
    """Health check endpoint"""
    return {
        "message": "Assignment Platform API",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "supabase",
        "upload_dir": settings.UPLOAD_DIR
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
