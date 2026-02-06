"""
Student Dashboard Page
"""
import streamlit as st
import sys
sys.path.append("..")

from components.auth import require_auth, logout
from utils.supabase_api import api

st.set_page_config(page_title="Student Dashboard", page_icon="📊", layout="wide")

from utils.rbac import check_access
from components.sidebar import render_sidebar

if not check_access(["student"]):
    st.stop()

render_sidebar()

user = st.session_state.user

st.title("📊 My Dashboard")
st.markdown(f"Welcome back, **{user.get('name')}**!")

st.markdown("---")

# Fetch data
assignments = api.list_assignments()
submissions = api.list_submissions()

# Stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📝 Assignments", len(assignments))

with col2:
    st.metric("📤 Submitted", len(submissions))

with col3:
    reviewed = [s for s in submissions if s.get("status") == "reviewed"]
    st.metric("✅ Graded", len(reviewed))

with col4:
    # Calculate average marks
    total_marks = sum(s.get("marks", 0) for s in reviewed if s.get("marks"))
    avg = total_marks / len(reviewed) if reviewed else 0
    st.metric("📈 Avg Score", f"{avg:.1f}")

st.markdown("---")

# Recent Submissions
st.subheader("📋 Recent Submissions")

if not submissions:
    st.info("You haven't submitted any assignments yet. Go to 'Submit Assignment' to get started!")
else:
    for sub in submissions[:5]:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            
            with col1:
                st.markdown(f"**{sub.get('assignment_title', 'Unknown Assignment')}**")
            
            with col2:
                file_type = sub.get('file_type', 'N/A').upper()
                st.markdown(f"📄 {file_type}")
            
            with col3:
                status = sub.get('status', 'pending')
                if status == "reviewed":
                    marks = sub.get('marks')
                    if marks is not None:
                        st.markdown(f"✅ **{marks}** marks")
                    else:
                        st.markdown("✅ Graded (no marks)")
                else:
                    st.markdown("🔄 Pending")
            
            with col4:
                submitted = sub.get('submitted_at', '')[:10]
                st.markdown(f"📅 {submitted}")
            
            st.markdown("---")

# Pending Assignments
st.subheader("⏳ Pending Assignments")

submitted_ids = [s.get('assignment_id') for s in submissions]
pending = [a for a in assignments if a.get('id') not in submitted_ids]

if not pending:
    st.success("🎉 You're all caught up! No pending assignments.")
else:
    for assign in pending:
        with st.container():
            col1, col2, col3 = st.columns([4, 2, 2])
            
            with col1:
                st.markdown(f"**{assign.get('title')}**")
                st.caption(assign.get('description', '')[:100])
            
            with col2:
                due = assign.get('due_date', '')[:10] if assign.get('due_date') else 'No deadline'
                st.markdown(f"📅 Due: {due}")
            
            with col3:
                max_marks = assign.get('max_marks', 100)
                st.markdown(f"🎯 Max: {max_marks}")
            
            st.markdown("---")
