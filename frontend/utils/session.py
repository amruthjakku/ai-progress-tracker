"""
Session Management Utility
"""
import streamlit as st
import extra_streamlit_components as stx
import datetime

def get_manager():
    """Get cookie manager instance - uses session state to ensure single instance"""
    if "_cookie_manager" not in st.session_state:
        st.session_state._cookie_manager = stx.CookieManager()
    return st.session_state._cookie_manager

def get_cookie(name):
    cookie_manager = get_manager()
    cookies = cookie_manager.get_all()
    return cookies.get(name)

def set_cookie(name, value, days=7):
    cookie_manager = get_manager()
    expires = datetime.datetime.now() + datetime.timedelta(days=days)
    cookie_manager.set(name, value, expires_at=expires)

def delete_cookie(name):
    cookie_manager = get_manager()
    cookie_manager.delete(name)
