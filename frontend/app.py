"""
Assignment Platform - Main Streamlit App
"""
import streamlit as st
from components.auth import show_auth_page, require_auth, logout

# Page configuration
st.set_page_config(
    page_title="Assignment Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .status-pending {
        background-color: #ffeaa7;
        color: #d63031;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.85rem;
    }
    .status-reviewed {
        background-color: #55efc4;
        color: #00b894;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

# Check authentication
if not require_auth():
    show_auth_page()
else:
    # Sidebar
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
    
    # Main content - Welcome page
    st.markdown('<p class="main-header">🎓 Assignment Platform</p>', unsafe_allow_html=True)
    
    if role == "admin":
        st.markdown("""
        ### Welcome, Admin!
        
        Use the sidebar to:
        - 📊 **Dashboard** - View overall statistics
        - 📝 **Manage Assignments** - Create and manage assignments
        - ✅ **Review Submissions** - Grade student work with file preview
        """)
    else:
        st.markdown("""
        ### Welcome, Student!
        
        Use the sidebar to:
        - 📊 **Dashboard** - View your submission overview
        - 📤 **Submit Assignment** - Upload your work
        - 📈 **My Grades** - View your grades and feedback
        """)
    
    # Quick stats
    from utils.api import api
    
    st.markdown("---")
    st.subheader("📊 Quick Overview")
    
    col1, col2, col3 = st.columns(3)
    
    assignments = api.list_assignments()
    submissions = api.list_submissions()
    
    with col1:
        st.metric("Total Assignments", len(assignments))
    
    with col2:
        if role == "admin":
            st.metric("Total Submissions", len(submissions))
        else:
            st.metric("My Submissions", len(submissions))
    
    with col3:
        reviewed = [s for s in submissions if s.get("status") == "reviewed"]
        if role == "admin":
            st.metric("Reviewed", len(reviewed))
        else:
            pending = len(submissions) - len(reviewed)
            st.metric("Pending Review", pending)
