"""
Submissions Router - File upload and submission management
"""
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import List
import os
import uuid
from datetime import datetime

from database import get_db
from schemas import SubmissionResponse, SubmissionWithDetails, TokenData, UserRole, SubmissionStatus
from utils.auth import get_current_user, require_admin
from config import get_settings

settings = get_settings()
router = APIRouter(prefix="/submissions", tags=["Submissions"])

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """Extract file extension"""
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


@router.post("/", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def submit_assignment(
    assignment_id: int = Form(...),
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user)
):
    """Submit an assignment with file upload"""
    db = get_db()
    
    # Validate file extension
    ext = get_file_extension(file.filename)
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Check assignment exists
    assignment = db.table("assignments").select("id").eq("id", assignment_id).execute()
    if not assignment.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Check if already submitted
    existing = db.table("submissions").select("id").eq("assignment_id", assignment_id).eq("student_id", current_user.user_id).execute()
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted this assignment"
        )
    
    # Save file
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create submission record
    result = db.table("submissions").insert({
        "assignment_id": assignment_id,
        "student_id": current_user.user_id,
        "file_path": unique_filename,
        "file_type": ext,
        "status": SubmissionStatus.PENDING.value
    }).execute()
    
    if not result.data:
        # Clean up file on failure
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create submission"
        )
    
    return result.data[0]


@router.get("/", response_model=List[SubmissionWithDetails])
def list_submissions(
    skip: int = 0,
    limit: int = 100,
    current_user: TokenData = Depends(get_current_user)
):
    """List submissions - students see own, admins see all"""
    db = get_db()
    
    if current_user.role == UserRole.ADMIN:
        # Admin sees all submissions with student info
        result = db.table("submissions").select(
            "*, users!student_id(name), assignments!assignment_id(title), reviews(*)"
        ).order("submitted_at", desc=True).range(skip, skip + limit - 1).execute()
    else:
        # Student sees only their submissions
        result = db.table("submissions").select(
            "*, assignments!assignment_id(title), reviews(*)"
        ).eq("student_id", current_user.user_id).order("submitted_at", desc=True).range(skip, skip + limit - 1).execute()
    
    # Transform response
    submissions = []
    for sub in result.data:
        reviews = sub.get("reviews")
        marks = None
        feedback = None
        
        # Safely extract review data
        if reviews and isinstance(reviews, list) and len(reviews) > 0:
            first_review = reviews[0]
            if isinstance(first_review, dict):
                marks = first_review.get("marks")
                feedback = first_review.get("feedback")
        
        submission = {
            **sub,
            "student_name": sub.get("users", {}).get("name") if sub.get("users") else None,
            "assignment_title": sub.get("assignments", {}).get("title") if sub.get("assignments") else None,
            "marks": marks,
            "feedback": feedback,
        }
        submissions.append(submission)
    
    return submissions


@router.get("/{submission_id}", response_model=SubmissionWithDetails)
def get_submission(
    submission_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    """Get a specific submission"""
    db = get_db()
    
    query = db.table("submissions").select(
        "*, users!student_id(name), assignments!assignment_id(title, max_marks), reviews(*)"
    ).eq("id", submission_id)
    
    # Students can only view their own
    if current_user.role != UserRole.ADMIN:
        query = query.eq("student_id", current_user.user_id)
    
    result = query.execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    sub = result.data[0]
    return {
        **sub,
        "student_name": sub.get("users", {}).get("name") if sub.get("users") else None,
        "assignment_title": sub.get("assignments", {}).get("title") if sub.get("assignments") else None,
        "marks": sub.get("reviews", [{}])[0].get("marks") if sub.get("reviews") else None,
        "feedback": sub.get("reviews", [{}])[0].get("feedback") if sub.get("reviews") else None,
    }
