"""
Grading Component - Mark allocation and feedback
"""
import streamlit as st
from utils.supabase_api import api


def show_grading_form(submission_id: int, max_marks: int = 100, current_marks: int = None, current_feedback: str = None):
    """
    Display grading form for a submission
    
    Args:
        submission_id: ID of the submission to grade
        max_marks: Maximum marks for the assignment
        current_marks: Existing marks if already reviewed
        current_feedback: Existing feedback if already reviewed
    """
    is_update = current_marks is not None
    
    if is_update:
        st.subheader("✏️ Update Grade")
        st.info(f"Current grade: **{current_marks}/{max_marks}**")
    else:
        st.subheader("📝 Grade Submission")
    
    with st.form(f"grading_form_{submission_id}"):
        # Marks input
        marks = st.number_input(
            "Marks",
            min_value=0,
            max_value=max_marks,
            value=current_marks if current_marks is not None else 0,
            help=f"Enter marks out of {max_marks}"
        )
        
        # Marks slider for quick selection
        marks_slider = st.slider(
            "Quick select",
            min_value=0,
            max_value=max_marks,
            value=marks,
            label_visibility="collapsed"
        )
        
        # Feedback textarea
        feedback = st.text_area(
            "Feedback",
            value=current_feedback or "",
            placeholder="Enter feedback for the student...",
            height=150
        )
        
        # Quick feedback buttons
        st.markdown("**Quick Feedback:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.form_submit_button("👍 Excellent", use_container_width=True):
                feedback = "Excellent work! Keep it up."
        
        with col2:
            if st.form_submit_button("👌 Good", use_container_width=True):
                feedback = "Good effort. Minor improvements needed."
        
        with col3:
            if st.form_submit_button("📝 Needs Work", use_container_width=True):
                feedback = "Needs significant improvement. Please review the requirements."
        
        st.markdown("---")
        
        # Submit button
        button_text = "💾 Update Grade" if is_update else "💾 Save Grade"
        submitted = st.form_submit_button(button_text, use_container_width=True, type="primary")
        
        if submitted:
            result = api.create_review(submission_id, marks_slider, feedback)
            
            if "error" in result:
                st.error(result["error"])
            else:
                st.success("✅ Grade saved successfully!")
                st.rerun()


def show_grade_badge(marks: int, max_marks: int):
    """Display a colored badge based on marks percentage"""
    if marks is None:
        st.markdown("🔄 **Pending Review**")
        return
    
    percentage = (marks / max_marks) * 100 if max_marks > 0 else 0
    
    if percentage >= 90:
        color = "green"
        label = "Excellent"
    elif percentage >= 75:
        color = "blue"
        label = "Good"
    elif percentage >= 60:
        color = "orange"
        label = "Average"
    elif percentage >= 40:
        color = "red"
        label = "Below Average"
    else:
        color = "darkred"
        label = "Poor"
    
    st.markdown(f"""
    <div style="
        background-color: {color};
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        display: inline-block;
        font-weight: bold;
    ">
        {marks}/{max_marks} - {label}
    </div>
    """, unsafe_allow_html=True)
