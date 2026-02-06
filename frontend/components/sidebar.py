"""
Shared Sidebar Component
"""
import streamlit as st
from components.auth import logout


def render_sidebar():
    """Render the sidebar with user info and navigation"""
    if "user" not in st.session_state or not st.session_state.user:
        return
    
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user.get('name', 'User')}")
        role = st.session_state.user.get('role', 'student')
        st.markdown(f"*{role.capitalize()}*")
        st.markdown("---")
        
        # Navigation
        if role == "admin":
            st.page_link("pages/1_Admin_Dashboard.py", label="📊 Dashboard", icon="📊")
            st.page_link("pages/2_Manage_Assignments.py", label="📝 Manage Assignments", icon="📝")
            st.page_link("pages/3_Review_Submissions.py", label="✅ Review Submissions", icon="✅")
        else:
            st.page_link("pages/1_Student_Dashboard.py", label="📊 My Dashboard", icon="📊")
            st.page_link("pages/2_Submit_Assignment.py", label="📤 Submit Assignment", icon="📤")
            st.page_link("pages/3_My_Grades.py", label="📈 My Grades", icon="📈")
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()
