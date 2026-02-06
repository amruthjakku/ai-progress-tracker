"""
Assignments Router - CRUD operations for assignments
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from database import get_db
from schemas import AssignmentCreate, AssignmentResponse, TokenData
from utils.auth import get_current_user, require_admin

router = APIRouter(prefix="/assignments", tags=["Assignments"])


@router.post("/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_assignment(
    assignment: AssignmentCreate,
    current_user: TokenData = Depends(require_admin)
):
    """Create a new assignment (admin only)"""
    db = get_db()
    
    result = db.table("assignments").insert({
        "title": assignment.title,
        "description": assignment.description,
        "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
        "max_marks": assignment.max_marks,
        "created_by": current_user.user_id
    }).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create assignment"
        )
    
    return result.data[0]


@router.get("/", response_model=List[AssignmentResponse])
def list_assignments(
    skip: int = 0,
    limit: int = 100,
    current_user: TokenData = Depends(get_current_user)
):
    """List all assignments with pagination"""
    db = get_db()
    result = db.table("assignments").select("*").order("created_at", desc=True).range(skip, skip + limit - 1).execute()
    return result.data


@router.get("/{assignment_id}", response_model=AssignmentResponse)
def get_assignment(
    assignment_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    """Get a specific assignment"""
    db = get_db()
    result = db.table("assignments").select("*").eq("id", assignment_id).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    return result.data[0]


@router.put("/{assignment_id}", response_model=AssignmentResponse)
def update_assignment(
    assignment_id: int,
    assignment: AssignmentCreate,
    current_user: TokenData = Depends(require_admin)
):
    """Update an assignment (admin only)"""
    db = get_db()
    
    result = db.table("assignments").update({
        "title": assignment.title,
        "description": assignment.description,
        "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
        "max_marks": assignment.max_marks
    }).eq("id", assignment_id).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    return result.data[0]


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment(
    assignment_id: int,
    current_user: TokenData = Depends(require_admin)
):
    """Delete an assignment (admin only)"""
    db = get_db()
    db.table("assignments").delete().eq("id", assignment_id).execute()
