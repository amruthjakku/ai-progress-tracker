"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum


# ============ Enums ============
class UserRole(str, Enum):
    STUDENT = "student"
    ADMIN = "admin"


class SubmissionStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"


# ============ User Schemas ============
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole = UserRole.STUDENT


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[UserRole] = None


# ============ Assignment Schemas ============
class AssignmentBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    max_marks: int = 100


class AssignmentCreate(AssignmentBase):
    pass


class AssignmentResponse(AssignmentBase):
    id: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Submission Schemas ============
class SubmissionBase(BaseModel):
    assignment_id: int


class SubmissionCreate(SubmissionBase):
    pass


class SubmissionResponse(SubmissionBase):
    id: int
    student_id: int
    file_path: str
    file_type: str
    submitted_at: datetime
    status: SubmissionStatus

    class Config:
        from_attributes = True


class SubmissionWithDetails(SubmissionResponse):
    student_name: Optional[str] = None
    assignment_title: Optional[str] = None
    marks: Optional[int] = None
    feedback: Optional[str] = None


# ============ Review Schemas ============
class ReviewBase(BaseModel):
    marks: int
    feedback: Optional[str] = None


class ReviewCreate(ReviewBase):
    submission_id: int


class ReviewResponse(ReviewBase):
    id: int
    submission_id: int
    reviewer_id: int
    reviewed_at: datetime

    class Config:
        from_attributes = True
