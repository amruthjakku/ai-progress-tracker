"""
Manage Assignments Page - Create and manage assignments (Admin only)
"""
import streamlit as st
from datetime import datetime, timedelta
import sys
sys.path.append("..")

from utils.api import api
from utils.rbac import check_access
from components.sidebar import render_sidebar

if not check_access(["admin"]):
    st.stop()

render_sidebar()

st.title("📝 Manage Assignments")

st.markdown("---")

# Create new assignment
st.subheader("➕ Create New Assignment")

with st.form("create_assignment"):
    title = st.text_input("Assignment Title", placeholder="e.g., Week 1 - Introduction to Python")
    description = st.text_area("Description", placeholder="Describe what students need to submit...")
    
    col1, col2 = st.columns(2)
    with col1:
        due_date = st.date_input("Due Date", value=datetime.now() + timedelta(days=7))
    with col2:
        max_marks = st.number_input("Maximum Marks", min_value=1, max_value=1000, value=100)
    
    submitted = st.form_submit_button("📤 Create Assignment", use_container_width=True, type="primary")
    
    if submitted:
        if not title:
            st.error("Please provide an assignment title")
        else:
            result = api.create_assignment(
                title=title,
                description=description,
                due_date=due_date.isoformat() if due_date else None,
                max_marks=max_marks
            )
            
            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                st.success("✅ Assignment created successfully!")
                st.rerun()

st.markdown("---")

# List existing assignments
st.subheader("📋 Existing Assignments")

assignments = api.list_assignments()

if not assignments:
    st.info("No assignments created yet. Use the form above to create one.")
else:
    for assign in assignments:
        with st.container():
            col1, col2, col3, col4 = st.columns([4, 2, 2, 1])
            
            with col1:
                st.markdown(f"### {assign.get('title')}")
                st.caption(assign.get('description', 'No description')[:100])
            
            with col2:
                due = assign.get('due_date', '')[:10] if assign.get('due_date') else 'No deadline'
                st.markdown(f"📅 **Due:** {due}")
            
            with col3:
                st.markdown(f"🎯 **Max Marks:** {assign.get('max_marks', 100)}")
            
            with col4:
                if st.button("🗑️", key=f"delete_{assign.get('id')}", help="Delete assignment"):
                    result = api.delete_assignment(assign.get('id'))
                    if "error" not in result:
                        st.success("Deleted!")
                        st.rerun()
                    else:
                        st.error(result["error"])
            
            st.markdown("---")
