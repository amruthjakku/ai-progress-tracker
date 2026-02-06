
import streamlit as st
import time

def check_access(allowed_roles):
    """
    Check if current user has access to this page.
    If not, show error and redirect to main app.
    """
    if "user" not in st.session_state or not st.session_state.user:
        st.error("Please login to access this page")
        time.sleep(1)
        st.switch_page("app.py")
        return False
    
    # Force hide sidebar on all protected pages
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

        
    user_role = st.session_state.user.get("role", "student")
    
    if user_role not in allowed_roles:
        st.error(f"⛔ Access Denied. This page is only for {', '.join(allowed_roles)}s.")
        time.sleep(2)
        st.switch_page("app.py")
        return False
        
    return True
