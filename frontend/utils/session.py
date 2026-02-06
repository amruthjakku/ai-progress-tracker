"""
Session Management Utility
"""
import streamlit as st
import extra_streamlit_components as stx
import datetime

def get_manager():
    """Get cookie manager instance - must be called on each script run"""
    return stx.CookieManager()

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
