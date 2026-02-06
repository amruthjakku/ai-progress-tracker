"""
Submit Assignment Page
"""
import streamlit as st
import sys
sys.path.append("..")

from components.auth import require_auth
from utils.api import api

st.set_page_config(page_title="Submit Assignment", page_icon="📤", layout="wide")

from utils.rbac import check_access
from components.sidebar import render_sidebar

if not check_access(["student"]):
    st.stop()

render_sidebar()

user = st.session_state.user

st.title("📤 Submit Assignment")

# Fetch assignments
assignments = api.list_assignments()
submissions = api.list_submissions()
submitted_ids = [s.get('assignment_id') for s in submissions]

# Filter out already submitted
available = [a for a in assignments if a.get('id') not in submitted_ids]

if not available:
    st.info("🎉 You've submitted all available assignments!")
    st.stop()

st.markdown("---")

# Assignment selection
st.subheader("Select Assignment")

selected_id = st.selectbox(
    "Choose an assignment to submit",
    options=[a.get('id') for a in available],
    format_func=lambda x: next((a.get('title') for a in available if a.get('id') == x), str(x))
)

# Show assignment details
selected = next((a for a in available if a.get('id') == selected_id), None)

if selected:
    with st.expander("📋 Assignment Details", expanded=True):
        st.markdown(f"### {selected.get('title')}")
        st.markdown(selected.get('description', 'No description provided.'))
        
        col1, col2 = st.columns(2)
        with col1:
            due = selected.get('due_date', '')[:10] if selected.get('due_date') else 'No deadline'
            st.info(f"📅 **Due Date:** {due}")
        with col2:
            st.info(f"🎯 **Max Marks:** {selected.get('max_marks', 100)}")

st.markdown("---")

# File upload
st.subheader("Upload Your Work")

st.markdown("""
**Supported file types:**
- 📕 PDF (.pdf)
- 📘 Word Documents (.docx)
- 📗 PowerPoint (.pptx, .ppt)
""")

uploaded_file = st.file_uploader(
    "Choose a file",
    type=["pdf", "docx", "pptx", "ppt"],
    help="Maximum file size: 10MB"
)

if uploaded_file:
    # Show file info
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**File:** {uploaded_file.name}")
    with col2:
        size_mb = uploaded_file.size / (1024 * 1024)
        st.markdown(f"**Size:** {size_mb:.2f} MB")
    
    st.markdown("---")
    
    # Submit button
    if st.button("🚀 Submit Assignment", type="primary", use_container_width=True):
        with st.spinner("Uploading..."):
            result = api.submit_assignment(selected_id, uploaded_file)
            
            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                st.success("✅ Assignment submitted successfully!")
                st.balloons()
                st.info("You can view your submission in 'My Grades' section.")
