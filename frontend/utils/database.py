"""
Supabase Database Connection
"""
import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def get_db() -> Client:
    """Get Supabase client instance (cached)"""
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
    return create_client(supabase_url, supabase_key)
