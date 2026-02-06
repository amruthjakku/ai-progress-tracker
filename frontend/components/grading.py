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
    
    # Initialize session state for marks if not exists
    if f"marks_{submission_id}" not in st.session_state:
        st.session_state[f"marks_{submission_id}"] = current_marks if current_marks is not None else 0
    
    # Callback to sync slider -> number
    def update_from_slider():
        st.session_state[f"marks_{submission_id}"] = st.session_state[f"slider_{submission_id}"]

    # Callback to sync number -> slider
    def update_from_number():
        st.session_state[f"marks_{submission_id}"] = st.session_state[f"number_{submission_id}"]

    # Container for the grading interface
    st.markdown("### 📝 Grade Submission")
    if is_update:
        st.info(f"Current grade: **{current_marks}/{max_marks}**")

    # Marks Input (Number)
    marks = st.number_input(
        "Marks",
        min_value=0,
        max_value=max_marks,
        value=st.session_state[f"marks_{submission_id}"],
        key=f"number_{submission_id}",
        on_change=update_from_number,
        help=f"Enter marks out of {max_marks}"
    )
    
    # Marks Slider (Syncs with above)
    st.slider(
        "Quick select",
        min_value=0,
        max_value=max_marks,
        value=marks,
        key=f"slider_{submission_id}",
        on_change=update_from_slider,
        label_visibility="collapsed"
    )
    
    # Feedback
    feedback = st.text_area(
        "Feedback",
        value=current_feedback or "",
        placeholder="Enter feedback for the student...",
        height=150,
        key=f"feedback_{submission_id}"
    )
    
    # Quick feedback buttons
    st.markdown("**Quick Feedback:**")
    col1, col2, col3 = st.columns(3)
    
    # Using callbacks for quick feedback to update the text area immediately
    def set_feedback(text):
        st.session_state[f"feedback_{submission_id}"] = text

    with col1:
        st.button("👍 Excellent", use_container_width=True, on_click=set_feedback, args=("Excellent work! Keep it up.",), key=f"btn_ex_{submission_id}")
    
    with col2:
        st.button("👌 Good", use_container_width=True, on_click=set_feedback, args=("Good effort. Minor improvements needed.",), key=f"btn_good_{submission_id}")
    
    with col3:
        st.button("📝 Needs Work", use_container_width=True, on_click=set_feedback, args=("Needs significant improvement. Please review the requirements.",), key=f"btn_work_{submission_id}")
    
    st.markdown("---")
    
    # Submit button (outside form now)
    button_text = "💾 Update Grade" if is_update else "💾 Save Grade"
    if st.button(button_text, type="primary", use_container_width=True, key=f"submit_{submission_id}"):
        with st.spinner("Saving grade..."):
            result = api.create_review(submission_id, marks, feedback)
            
            if "error" in result:
                st.error(result["error"])
            else:
                st.success("✅ Grade saved successfully!")
                # Force reload of submissions to update UI immediately
                api.list_submissions.clear()
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
