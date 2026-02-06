"""
Supabase API Client - Direct database operations
Replaces the HTTP-based API client
"""
import streamlit as st
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt
import uuid

from utils.database import get_db


# Password hasher
ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a password using argon2"""
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False


def create_access_token(user_id: int, role: str) -> str:
    """Create JWT access token"""
    expire = datetime.utcnow() + timedelta(minutes=60 * 24 * 7)  # 7 days
    to_encode = {
        "sub": str(user_id),
        "role": role,
        "exp": expire
    }
    return jwt.encode(to_encode, st.secrets["JWT_SECRET"], algorithm="HS256")


def decode_token(token: str) -> Optional[Dict]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, st.secrets["JWT_SECRET"], algorithms=["HS256"])
        return {
            "user_id": int(payload.get("sub")),
            "role": payload.get("role")
        }
    except:
        return None


class SupabaseAPI:
    """Direct Supabase API client"""
    
    def __init__(self):
        self.db = get_db()
    
    def _get_current_user(self) -> Optional[Dict]:
        """Get current authenticated user from session"""
        return st.session_state.get("user")
    
    def _get_current_user_id(self) -> Optional[int]:
        """Get current user ID"""
        user = self._get_current_user()
        return user.get("id") if user else None
    
    def _is_admin(self) -> bool:
        """Check if current user is admin"""
        user = self._get_current_user()
        return user.get("role") == "admin" if user else False
    
    # ============ Auth ============
    def register(self, email: str, password: str, name: str, role: str = "student") -> Dict:
        """Register a new user"""
        try:
            # Check if user exists
            existing = self.db.table("users").select("id").eq("email", email).execute()
            if existing.data:
                return {"error": "Email already registered"}
            
            # Create user
            hashed_pw = hash_password(password)
            user_data = {
                "email": email,
                "name": name,
                "password_hash": hashed_pw,
            }
            if role != "student":
                user_data["role"] = role
            
            result = self.db.table("users").insert(user_data).execute()
            
            if not result.data:
                return {"error": "Failed to create user"}
            
            return result.data[0]
        except Exception as e:
            return {"error": f"Registration failed: {str(e)}"}
    
    def login(self, email: str, password: str) -> Dict:
        """Login and get access token"""
        try:
            # Find user
            result = self.db.table("users").select("*").eq("email", email).execute()
            if not result.data:
                return {"error": "Invalid email or password"}
            
            user = result.data[0]
            
            # Verify password
            if not verify_password(password, user["password_hash"]):
                return {"error": "Invalid email or password"}
            
            # Create token
            token = create_access_token(user["id"], user["role"])
            return {"access_token": token, "user": user}
        except Exception as e:
            return {"error": f"Login failed: {str(e)}"}
    
    def get_user(self, user_id: int) -> Dict:
        """Get user by ID"""
        try:
            result = self.db.table("users").select("*").eq("id", user_id).execute()
            if not result.data:
                return {"error": "User not found"}
            return result.data[0]
        except Exception as e:
            return {"error": str(e)}
    
    # ============ Assignments ============
    @st.cache_data(ttl=60)
    def list_assignments(_self) -> List[Dict]:
        """List all assignments"""
        try:
            result = _self.db.table("assignments").select("*").order("created_at", desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            st.error(f"Failed to load assignments: {e}")
            return []
    
    def create_assignment(self, title: str, description: str, due_date: str, max_marks: int) -> Dict:
        """Create a new assignment (admin only)"""
        try:
            self.list_assignments.clear()
            
            result = self.db.table("assignments").insert({
                "title": title,
                "description": description,
                "due_date": due_date,
                "max_marks": max_marks,
                "created_by": self._get_current_user_id()
            }).execute()
            
            if not result.data:
                return {"error": "Failed to create assignment"}
            return result.data[0]
        except Exception as e:
            return {"error": f"Failed to create assignment: {str(e)}"}
    
    def delete_assignment(self, assignment_id: int) -> Dict:
        """Delete an assignment"""
        try:
            self.list_assignments.clear()
            self.db.table("assignments").delete().eq("id", assignment_id).execute()
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}
    
    # ============ Submissions ============
    @st.cache_data(ttl=60)
    def list_submissions(_self) -> List[Dict]:
        """List submissions - filtered by role"""
        try:
            user = _self._get_current_user()
            if not user:
                return []
            
            if user.get("role") == "admin":
                # Admin sees all submissions with student info
                result = _self.db.table("submissions").select(
                    "*, users!student_id(name), assignments!assignment_id(title), reviews(*)"
                ).order("submitted_at", desc=True).execute()
            else:
                # Student sees only their own
                result = _self.db.table("submissions").select(
                    "*, assignments!assignment_id(title), reviews(*)"
                ).eq("student_id", user["id"]).order("submitted_at", desc=True).execute()
            
            # Transform response
            submissions = []
            for sub in result.data or []:
                reviews = sub.get("reviews")
                marks = None
                feedback = None
                
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
        except Exception as e:
            st.error(f"Failed to load submissions: {e}")
            return []
    
    def submit_assignment(self, assignment_id: int, file) -> Dict:
        """Submit an assignment with file upload"""
        try:
            self.list_submissions.clear()
            
            user_id = self._get_current_user_id()
            if not user_id:
                return {"error": "Not authenticated"}
            
            # Check if already submitted
            existing = self.db.table("submissions").select("id").eq(
                "assignment_id", assignment_id
            ).eq("student_id", user_id).execute()
            
            if existing.data:
                return {"error": "You have already submitted this assignment"}
            
            # Get file info
            file_name = file.name
            file_ext = file_name.split(".")[-1].lower()
            file_content = file.getvalue()
            
            # Generate unique filename
            unique_name = f"{user_id}_{assignment_id}_{uuid.uuid4().hex[:8]}_{file_name}"
            
            # Upload to Supabase Storage (just the path, not including bucket name)
            storage_path = unique_name
            
            try:
                self.db.storage.from_("submissions").upload(
                    storage_path,
                    file_content,
                    {"content-type": file.type}
                )
            except Exception as upload_error:
                # If bucket doesn't exist, try to handle gracefully
                return {"error": f"File upload failed: {str(upload_error)}. Make sure 'submissions' bucket exists in Supabase Storage."}
            
            # Create submission record
            result = self.db.table("submissions").insert({
                "student_id": user_id,
                "assignment_id": assignment_id,
                "file_path": storage_path,
                "file_type": file_ext,
                "status": "pending"
            }).execute()
            
            if not result.data:
                return {"error": "Failed to create submission record"}
            
            return result.data[0]
        except Exception as e:
            return {"error": f"Submission failed: {str(e)}"}
    
    # ============ Reviews ============
    def create_review(self, submission_id: int, marks: int, feedback: str) -> Dict:
        """Create or update a review"""
        try:
            self.list_submissions.clear()
            
            user_id = self._get_current_user_id()
            if not user_id:
                return {"error": "Not authenticated"}
            
            # Check if already reviewed
            existing = self.db.table("reviews").select("id").eq("submission_id", submission_id).execute()
            
            if existing.data:
                # Update existing
                result = self.db.table("reviews").update({
                    "marks": marks,
                    "feedback": feedback,
                    "reviewer_id": user_id
                }).eq("submission_id", submission_id).execute()
            else:
                # Create new
                result = self.db.table("reviews").insert({
                    "submission_id": submission_id,
                    "reviewer_id": user_id,
                    "marks": marks,
                    "feedback": feedback
                }).execute()
            
            if not result.data:
                return {"error": "Failed to save review"}
            
            # Update submission status
            self.db.table("submissions").update({
                "status": "reviewed"
            }).eq("id", submission_id).execute()
            
            return result.data[0]
        except Exception as e:
            return {"error": f"Review failed: {str(e)}"}
    
    # ============ Files ============
    def get_file_info(self, submission_id: int) -> Dict:
        """Get file metadata"""
        try:
            result = self.db.table("submissions").select("*").eq("id", submission_id).execute()
            if not result.data:
                return {"error": "Submission not found"}
            
            sub = result.data[0]
            return {
                "file_type": sub.get("file_type"),
                "file_path": sub.get("file_path")
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_file_url(self, submission_id: int) -> Optional[str]:
        """Get signed URL for file download/preview"""
        try:
            result = self.db.table("submissions").select("file_path").eq("id", submission_id).execute()
            if not result.data:
                return None
            
            file_path = result.data[0].get("file_path")
            if not file_path:
                return None
            
            # Handle old file paths that may have different formats
            # Remove 'submissions/' prefix if present (from old format)
            if file_path.startswith("submissions/"):
                file_path = file_path[len("submissions/"):]
            # Also handle 'uploads/' prefix from legacy backend
            elif file_path.startswith("uploads/"):
                file_path = file_path[len("uploads/"):]
            
            # Get signed URL (valid for 1 hour)
            url_data = self.db.storage.from_("submissions").create_signed_url(file_path, 3600)
            return url_data.get("signedURL") if url_data else None
        except Exception as e:
            st.error(f"Failed to get file URL: {e}")
            return None


# Singleton instance
api = SupabaseAPI()
