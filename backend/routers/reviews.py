"""
Reviews Router - Grade submissions and provide feedback
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from database import get_db
from schemas import ReviewCreate, ReviewResponse, TokenData, SubmissionStatus
from utils.auth import require_admin

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    current_user: TokenData = Depends(require_admin)
):
    """Create a review for a submission (admin only)"""
    db = get_db()
    
    # Check submission exists and get max marks
    submission = db.table("submissions").select(
        "*, assignments!assignment_id(max_marks)"
    ).eq("id", review.submission_id).execute()
    
    if not submission.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    max_marks = submission.data[0].get("assignments", {}).get("max_marks", 100)
    
    # Validate marks
    if review.marks < 0 or review.marks > max_marks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Marks must be between 0 and {max_marks}"
        )
    
    # Check if already reviewed
    existing = db.table("reviews").select("id").eq("submission_id", review.submission_id).execute()
    if existing.data:
        # Update existing review
        result = db.table("reviews").update({
            "marks": review.marks,
            "feedback": review.feedback,
            "reviewer_id": current_user.user_id
        }).eq("submission_id", review.submission_id).execute()
    else:
        # Create new review
        result = db.table("reviews").insert({
            "submission_id": review.submission_id,
            "reviewer_id": current_user.user_id,
            "marks": review.marks,
            "feedback": review.feedback
        }).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create review"
        )
    
    # Update submission status to reviewed
    db.table("submissions").update({
        "status": SubmissionStatus.REVIEWED.value
    }).eq("id", review.submission_id).execute()
    
    return result.data[0]


@router.get("/submission/{submission_id}", response_model=ReviewResponse)
async def get_review_by_submission(
    submission_id: int,
    current_user: TokenData = Depends(require_admin)
):
    """Get review for a specific submission"""
    db = get_db()
    result = db.table("reviews").select("*").eq("submission_id", submission_id).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return result.data[0]
