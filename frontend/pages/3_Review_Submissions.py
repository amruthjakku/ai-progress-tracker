"""
Review Submissions Page - Grade student work with file preview (Admin only)
"""
import streamlit as st
import sys
sys.path.append("..")

from components.auth import require_auth, require_admin
from components.file_preview import show_file_preview, show_file_info
from components.grading import show_grading_form
from utils.api import api

st.set_page_config(page_title="Review Submissions", page_icon="✅", layout="wide")

from utils.rbac import check_access

if not check_access(["admin"]):
    st.stop()

st.title("✅ Review Submissions")

# Fetch submissions
submissions = api.list_submissions()

if not submissions:
    st.info("No submissions to review yet.")
    st.stop()

st.markdown("---")

# Filter options
col1, col2 = st.columns(2)

with col1:
    status_filter = st.selectbox(
        "Filter by Status",
        options=["all", "pending", "reviewed"],
        format_func=lambda x: x.capitalize()
    )

with col2:
    # Get unique assignments
    assignments = list(set(s.get('assignment_title', 'Unknown') for s in submissions))
    assignment_filter = st.selectbox(
        "Filter by Assignment",
        options=["All"] + assignments
    )

# Apply filters
filtered = submissions
if status_filter != "all":
    filtered = [s for s in filtered if s.get('status') == status_filter]
if assignment_filter != "All":
    filtered = [s for s in filtered if s.get('assignment_title') == assignment_filter]

st.markdown(f"**Showing {len(filtered)} submissions**")
st.markdown("---")

# Check if coming from dashboard with specific submission
if "review_submission_id" in st.session_state:
    selected_id = st.session_state.review_submission_id
    del st.session_state.review_submission_id
else:
    selected_id = None

# Submission list with review panel
for sub in filtered:
    sub_id = sub.get('id')
    is_expanded = selected_id == sub_id
    
    status_icon = "✅" if sub.get('status') == 'reviewed' else "🔄"
    header = f"{status_icon} {sub.get('student_name', 'Unknown')} - {sub.get('assignment_title', 'Unknown')}"
    
    with st.expander(header, expanded=is_expanded):
        # Two-column layout: Preview on left, grading on right
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("📄 File Preview")
            
            # File info
            show_file_info(sub_id)
            
            # Preview
            file_type = sub.get('file_type', 'pdf')
            
            # Initialize slide state for PPT
            if f"current_slide_{sub_id}" not in st.session_state:
                st.session_state[f"current_slide_{sub_id}"] = 1
            
            show_file_preview(sub_id, file_type, height=500)
            
            # Download option
            download_url = api.get_file_download_url(sub_id)
            st.markdown(f"[📥 Download Original File]({download_url})")
        
        with col2:
            st.markdown(f"**Student:** {sub.get('student_name', 'Unknown')}")
            st.markdown(f"**Submitted:** {sub.get('submitted_at', '')[:10]}")
            
            st.markdown("---")
            
            # Get max marks from assignment (default 100)
            max_marks = 100  # Could fetch from assignment
            
            show_grading_form(
                submission_id=sub_id,
                max_marks=max_marks,
                current_marks=sub.get('marks'),
                current_feedback=sub.get('feedback')
            )
