"""
API Client - Communicate with FastAPI backend
"""
import requests
from typing import Optional, Dict, Any, List
import streamlit as st
from config import API_URL


class APIClient:
    def __init__(self):
        self.base_url = API_URL
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with auth token if available"""
        headers = {"Content-Type": "application/json"}
        if "token" in st.session_state and st.session_state.token:
            headers["Authorization"] = f"Bearer {st.session_state.token}"
        return headers
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        # Handle file uploads separately
        if "files" in kwargs:
            headers.pop("Content-Type", None)
        
        try:
            response = requests.request(method, url, headers=headers, timeout=30, **kwargs)
            
            if response.status_code == 401:
                st.session_state.token = None
                st.session_state.user = None
                return {"error": "Session expired. Please login again."}
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error = error_data.get("detail", str(error_data))
                except:
                    error = f"Server error ({response.status_code}): {response.text[:200] if response.text else 'No response'}"
                return {"error": error}
            
            if response.status_code == 204:
                return {"success": True}
            
            # Handle empty response
            if not response.text:
                return {"error": "Server returned empty response"}
            
            return response.json()
        except requests.exceptions.ConnectionError:
            return {"error": "Cannot connect to server. Is the backend running at http://localhost:8000?"}
        except requests.exceptions.JSONDecodeError as e:
            return {"error": f"Invalid response from server: {str(e)}"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    # ============ Auth ============
    def register(self, email: str, password: str, name: str, role: str = "student") -> Dict:
        return self._request("POST", "/auth/register", json={
            "email": email,
            "password": password,
            "name": name,
            "role": role
        })
    
    def login(self, email: str, password: str) -> Dict:
        return self._request("POST", "/auth/login", json={
            "email": email,
            "password": password
        })
    
    def get_me(self) -> Dict:
        return self._request("GET", "/auth/me")
    
    # ============ Assignments ============
    def list_assignments(self) -> List[Dict]:
        result = self._request("GET", "/assignments/")
        return result if isinstance(result, list) else []
    
    def create_assignment(self, title: str, description: str, due_date: str, max_marks: int) -> Dict:
        return self._request("POST", "/assignments/", json={
            "title": title,
            "description": description,
            "due_date": due_date,
            "max_marks": max_marks
        })
    
    def delete_assignment(self, assignment_id: int) -> Dict:
        return self._request("DELETE", f"/assignments/{assignment_id}")
    
    # ============ Submissions ============
    def list_submissions(self) -> List[Dict]:
        result = self._request("GET", "/submissions/")
        return result if isinstance(result, list) else []
    
    def get_submission(self, submission_id: int) -> Dict:
        return self._request("GET", f"/submissions/{submission_id}")
    
    def submit_assignment(self, assignment_id: int, file) -> Dict:
        return self._request(
            "POST", 
            "/submissions/",
            data={"assignment_id": str(assignment_id)},
            files={"file": (file.name, file.getvalue(), file.type)}
        )
    
    # ============ Reviews ============
    def create_review(self, submission_id: int, marks: int, feedback: str) -> Dict:
        return self._request("POST", "/reviews/", json={
            "submission_id": submission_id,
            "marks": marks,
            "feedback": feedback
        })
    
    # ============ Files ============
    def get_file_info(self, submission_id: int) -> Dict:
        return self._request("GET", f"/files/preview/{submission_id}/info")
    
    def get_file_preview_url(self, submission_id: int, page: Optional[int] = None) -> str:
        url = f"{self.base_url}/files/preview/{submission_id}"
        if page:
            url += f"?page={page}"
        return url
    
    def get_file_download_url(self, submission_id: int) -> str:
        return f"{self.base_url}/files/download/{submission_id}"


# Singleton instance
api = APIClient()
