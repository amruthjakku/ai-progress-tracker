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
    version="1.0.0"
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


@app.get("/")
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
