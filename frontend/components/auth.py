"""
Authentication Components - Login & Register forms
"""
import streamlit as st
from utils.api import api


def show_login_form():
    """Display login form"""
    st.subheader("🔐 Login")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            if not email or not password:
                st.error("Please fill in all fields")
                return
            
            result = api.login(email, password)
            
            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state.token = result["access_token"]
                # Fetch user profile
                user = api.get_me()
                if "error" not in user:
                    st.session_state.user = user
                    st.success("Login successful!")
                    st.rerun()


def show_register_form():
    """Display registration form"""
    st.subheader("📝 Register")
    
    with st.form("register_form"):
        name = st.text_input("Full Name", placeholder="John Doe")
        email = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        role = st.selectbox("Role", ["student", "admin"])
        
        submit = st.form_submit_button("Register", use_container_width=True)
        
        if submit:
            if not all([name, email, password, confirm_password]):
                st.error("Please fill in all fields")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            
            if len(password) < 6:
                st.error("Password must be at least 6 characters")
                return
            
            result = api.register(email, password, name, role)
            
            if "error" in result:
                st.error(result["error"])
            else:
                st.success("Registration successful! Please login.")


def show_auth_page():
    """Display authentication page with login/register tabs"""
    st.title("🎓 Assignment Platform")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        show_login_form()
    
    with tab2:
        show_register_form()


def logout():
    """Clear session and logout"""
    st.session_state.token = None
    st.session_state.user = None
    st.rerun()


def require_auth():
    """Check if user is authenticated"""
    if "token" not in st.session_state or not st.session_state.token:
        return False
    if "user" not in st.session_state or not st.session_state.user:
        return False
    return True


def require_admin():
    """Check if user is admin"""
    if not require_auth():
        return False
    return st.session_state.user.get("role") == "admin"
