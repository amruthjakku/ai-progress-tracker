"""
Admin Dashboard Page
"""
import streamlit as st
import sys
sys.path.append("..")

from components.auth import require_auth, require_admin
from utils.api import api

st.set_page_config(page_title="Admin Dashboard", page_icon="📊", layout="wide")

if not require_auth():
    st.warning("Please login to access this page")
    st.stop()

if not require_admin():
    st.error("⛔ Admin access required")
    st.stop()

user = st.session_state.user

st.title("📊 Admin Dashboard")
st.markdown(f"Welcome, **{user.get('name')}**!")

st.markdown("---")

# Fetch data
assignments = api.list_assignments()
submissions = api.list_submissions()

# Stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📝 Assignments", len(assignments))

with col2:
    st.metric("📤 Submissions", len(submissions))

with col3:
    reviewed = [s for s in submissions if s.get("status") == "reviewed"]
    st.metric("✅ Reviewed", len(reviewed))

with col4:
    pending = [s for s in submissions if s.get("status") == "pending"]
    st.metric("🔄 Pending Review", len(pending), delta=f"-{len(pending)}" if pending else None)

st.markdown("---")

# Recent Submissions needing review
st.subheader("🔔 Pending Reviews")

if not pending:
    st.success("🎉 All submissions have been reviewed!")
else:
    for sub in pending[:5]:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            
            with col1:
                st.markdown(f"**{sub.get('student_name', 'Unknown Student')}**")
                st.caption(sub.get('assignment_title', 'Unknown Assignment'))
            
            with col2:
                file_type = sub.get('file_type', 'N/A').upper()
                st.markdown(f"📄 {file_type}")
            
            with col3:
                submitted = sub.get('submitted_at', '')[:10]
                st.markdown(f"📅 {submitted}")
            
            with col4:
                if st.button("Review →", key=f"review_{sub.get('id')}"):
                    st.session_state.review_submission_id = sub.get('id')
                    st.switch_page("pages/3_Review_Submissions.py")
            
            st.markdown("---")

# Assignment Overview
st.subheader("📈 Assignment Statistics")

if assignments:
    for assign in assignments:
        assign_id = assign.get('id')
        assign_subs = [s for s in submissions if s.get('assignment_id') == assign_id]
        reviewed_subs = [s for s in assign_subs if s.get('status') == 'reviewed']
        
        with st.expander(f"📝 {assign.get('title')}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Submissions", len(assign_subs))
            with col2:
                st.metric("Reviewed", len(reviewed_subs))
            with col3:
                if reviewed_subs:
                    avg = sum(s.get('marks', 0) for s in reviewed_subs) / len(reviewed_subs)
                    st.metric("Avg Score", f"{avg:.1f}")
                else:
                    st.metric("Avg Score", "N/A")
            
            # Progress bar
            if assign_subs:
                progress = len(reviewed_subs) / len(assign_subs)
                st.progress(progress, text=f"Review Progress: {progress*100:.0f}%")
else:
    st.info("No assignments created yet. Go to 'Manage Assignments' to create one.")
