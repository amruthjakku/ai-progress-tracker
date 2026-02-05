"""
My Grades Page - View submission grades and feedback
"""
import streamlit as st
import sys
sys.path.append("..")

from components.auth import require_auth
from components.file_preview import show_file_preview, show_file_info
from components.grading import show_grade_badge
from utils.api import api

st.set_page_config(page_title="My Grades", page_icon="📈", layout="wide")

if not require_auth():
    st.warning("Please login to access this page")
    st.stop()

user = st.session_state.user
if user.get("role") != "student":
    st.error("This page is for students only")
    st.stop()

st.title("📈 My Grades")

# Fetch submissions
submissions = api.list_submissions()

if not submissions:
    st.info("You haven't submitted any assignments yet.")
    st.stop()

st.markdown("---")

# Summary stats
reviewed = [s for s in submissions if s.get("status") == "reviewed"]
pending = [s for s in submissions if s.get("status") == "pending"]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📤 Total Submissions", len(submissions))
with col2:
    st.metric("✅ Graded", len(reviewed))
with col3:
    st.metric("🔄 Pending", len(pending))

st.markdown("---")

# Detailed view
st.subheader("📋 All Submissions")

for sub in submissions:
    with st.expander(f"📝 {sub.get('assignment_title', 'Unknown')} - {sub.get('status', 'pending').upper()}"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**Submitted:** {sub.get('submitted_at', '')[:10]}")
            st.markdown(f"**File Type:** {sub.get('file_type', 'N/A').upper()}")
            
            if sub.get("status") == "reviewed":
                st.markdown("---")
                st.markdown("### Grade")
                show_grade_badge(sub.get('marks'), 100)  # Assuming max 100
                
                if sub.get('feedback'):
                    st.markdown("### Feedback")
                    st.info(sub.get('feedback'))
            else:
                st.warning("⏳ This submission is pending review.")
        
        with col2:
            st.markdown("### File Preview")
            show_file_info(sub.get('id'))
            
            if st.button("👁️ Preview File", key=f"preview_{sub.get('id')}"):
                st.session_state[f"show_preview_{sub.get('id')}"] = True
        
        # Show preview if requested
        if st.session_state.get(f"show_preview_{sub.get('id')}"):
            st.markdown("---")
            show_file_preview(sub.get('id'), sub.get('file_type'))
