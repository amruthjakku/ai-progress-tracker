"""
Files Router - File preview endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import Response, StreamingResponse
import os
import io
import base64
from typing import Optional

from database import get_db
from schemas import TokenData, UserRole
from utils.auth import get_current_user
from config import get_settings
from services.file_preview import get_file_preview, get_preview_content_type

settings = get_settings()
router = APIRouter(prefix="/files", tags=["Files"])


@router.get("/preview/{submission_id}")
async def preview_file(
    submission_id: int,
    page: Optional[int] = None,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get file preview for a submission
    - PDF: Returns the PDF for iframe embedding
    - DOCX: Returns HTML content
    - PPT/PPTX: Returns slide images
    """
    db = get_db()
    
    # Get submission
    query = db.table("submissions").select("*").eq("id", submission_id)
    
    # Students can only view their own files
    if current_user.role != UserRole.ADMIN:
        query = query.eq("student_id", current_user.user_id)
    
    result = query.execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found or access denied"
        )
    
    submission = result.data[0]
    file_path = os.path.join(settings.UPLOAD_DIR, submission["file_path"])
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )
    
    # Get preview content
    try:
        preview_data = get_file_preview(file_path, submission["file_type"], page)
        content_type = get_preview_content_type(submission["file_type"])
        
        return Response(
            content=preview_data,
            media_type=content_type,
            headers={
                "Content-Disposition": f"inline; filename=preview.{submission['file_type']}"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate preview: {str(e)}"
        )


@router.get("/preview/{submission_id}/info")
async def get_file_info(
    submission_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    """Get file metadata for preview rendering"""
    db = get_db()
    
    query = db.table("submissions").select("*").eq("id", submission_id)
    
    if current_user.role != UserRole.ADMIN:
        query = query.eq("student_id", current_user.user_id)
    
    result = query.execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    submission = result.data[0]
    file_path = os.path.join(settings.UPLOAD_DIR, submission["file_path"])
    
    # Get file size and page count if applicable
    from services.file_preview import get_file_info as get_info
    file_info = get_info(file_path, submission["file_type"])
    
    return {
        "file_type": submission["file_type"],
        "original_name": submission["file_path"].split("_", 1)[1] if "_" in submission["file_path"] else submission["file_path"],
        **file_info
    }


@router.get("/download/{submission_id}")
async def download_file(
    submission_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    """Download the original file"""
    db = get_db()
    
    query = db.table("submissions").select("*").eq("id", submission_id)
    
    if current_user.role != UserRole.ADMIN:
        query = query.eq("student_id", current_user.user_id)
    
    result = query.execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    submission = result.data[0]
    file_path = os.path.join(settings.UPLOAD_DIR, submission["file_path"])
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Get original filename
    original_name = submission["file_path"].split("_", 1)[1] if "_" in submission["file_path"] else submission["file_path"]
    
    with open(file_path, "rb") as f:
        content = f.read()
    
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={original_name}"
        }
    )
