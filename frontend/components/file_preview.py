"""
File Preview Component - Display files in browser
"""
import streamlit as st
import streamlit.components.v1 as components
from utils.supabase_api import api


def show_file_preview(submission_id: int, file_type: str, height: int = 600):
    """
    Display file preview based on file type
    
    Args:
        submission_id: ID of the submission
        file_type: File extension (pdf, docx, pptx)
        height: Height of the preview component
    """
    preview_url = api.get_file_url(submission_id)
    
    if not preview_url:
        st.warning("File not available for preview")
        return
    
    if file_type == "pdf":
        # PDF: Use iframe with PDF viewer
        st.markdown(f"""
        <iframe 
            src="{preview_url}" 
            width="100%" 
            height="{height}px" 
            style="border: 1px solid #ddd; border-radius: 8px;"
        ></iframe>
        """, unsafe_allow_html=True)
        
    elif file_type == "docx":
        # DOCX: Download link (can't render in frontend without backend conversion)
        st.info("📄 Word documents can be previewed after download")
        st.markdown(f"[📥 Download Document]({preview_url})")
            
    elif file_type in ["pptx", "ppt"]:
        # PPT: Download link (can't render in frontend without backend conversion)
        st.info("📊 Presentations can be previewed after download")
        st.markdown(f"[📥 Download Presentation]({preview_url})")
    else:
        st.warning(f"Preview not available for {file_type} files")
        st.markdown(f"[📥 Download File]({preview_url})")


def show_file_info(submission_id: int):
    """Display file metadata"""
    file_info = api.get_file_info(submission_id)
    
    if "error" in file_info:
        st.error(file_info["error"])
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("File Type", file_info.get("file_type", "Unknown").upper())
    
    with col2:
        size_bytes = file_info.get("size_bytes", 0)
        if size_bytes > 1024 * 1024:
            size_str = f"{size_bytes / (1024*1024):.2f} MB"
        elif size_bytes > 1024:
            size_str = f"{size_bytes / 1024:.2f} KB"
        else:
            size_str = f"{size_bytes} bytes"
        st.metric("File Size", size_str)
    
    if "page_count" in file_info and file_info["page_count"] > 0:
        st.info(f"📄 {file_info['page_count']} pages")
    elif "slide_count" in file_info and file_info["slide_count"] > 0:
        st.info(f"📊 {file_info['slide_count']} slides")
