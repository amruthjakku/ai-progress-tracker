"""
File Preview Component - Display files in browser
"""
import streamlit as st
import streamlit.components.v1 as components
from utils.api import api
from config import API_URL


def show_file_preview(submission_id: int, file_type: str, height: int = 600):
    """
    Display file preview based on file type
    
    Args:
        submission_id: ID of the submission
        file_type: File extension (pdf, docx, pptx)
        height: Height of the preview component
    """
    preview_url = api.get_file_preview_url(submission_id)
    
    # Add auth header for preview
    token = st.session_state.get("token", "")
    
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
        # DOCX: Rendered as HTML
        try:
            import requests
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(preview_url, headers=headers)
            
            if response.status_code == 200:
                html_content = response.text
                components.html(html_content, height=height, scrolling=True)
            else:
                st.error("Failed to load document preview")
        except Exception as e:
            st.error(f"Error loading preview: {e}")
            
    elif file_type in ["pptx", "ppt"]:
        # PPT: Display as slides with navigation
        file_info = api.get_file_info(submission_id)
        slide_count = file_info.get("slide_count", 1)
        
        if slide_count > 0:
            # Slide navigation
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                if st.button("⬅️ Previous"):
                    if st.session_state.get("current_slide", 1) > 1:
                        st.session_state.current_slide -= 1
                        st.rerun()
            
            with col2:
                current = st.session_state.get("current_slide", 1)
                st.markdown(f"<center>Slide {current} of {slide_count}</center>", unsafe_allow_html=True)
            
            with col3:
                if st.button("Next ➡️"):
                    if st.session_state.get("current_slide", 1) < slide_count:
                        st.session_state.current_slide += 1
                        st.rerun()
            
            # Display current slide
            current_slide = st.session_state.get("current_slide", 1)
            slide_url = api.get_file_preview_url(submission_id, page=current_slide)
            
            try:
                import requests
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(slide_url, headers=headers)
                
                if response.status_code == 200:
                    st.image(response.content, use_container_width=True)
                else:
                    st.error("Failed to load slide")
            except Exception as e:
                st.error(f"Error loading slide: {e}")
    else:
        st.warning(f"Preview not available for {file_type} files")


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
