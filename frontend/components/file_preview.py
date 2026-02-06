"""
File Preview Component - Display files in browser
"""
import streamlit as st
import streamlit.components.v1 as components
import requests
import base64
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
        # PDF: Fetch and embed as base64 to avoid iframe blocking
        try:
            # Download PDF content
            response = requests.get(preview_url, timeout=30)
            if response.status_code == 200 and len(response.content) > 0:
                # Use PDF.js (Mozilla's PDF viewer) to render content directly via JavaScript
                # This bypasses browser PDF plugin restrictions and iframe sandbox issues
                pdf_viewer_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
                    <style>
                        body {{ margin: 0; padding: 0; background-color: #525659; display: flex; flex-direction: column; align-items: center; }}
                        #the-canvas {{ border: 1px solid black; direction: ltr; margin-bottom: 10px; }}
                        #controls {{ position: sticky; top: 0; background: #333; color: white; padding: 8px; width: 100%; text-align: center; z-index: 100; }}
                        button {{ cursor: pointer; padding: 5px 10px; background: #444; color: white; border: 1px solid #666; }}
                        button:hover {{ background: #555; }}
                    </style>
                </head>
                <body>
                    <div id="controls">
                        <button id="prev">Previous</button>
                        <span>Page: <span id="page_num"></span> / <span id="page_count"></span></span>
                        <button id="next">Next</button>
                        <a href="{preview_url}" target="_blank" style="color: white; margin-left: 10px; text-decoration: none;">Download</a>
                    </div>
                    <canvas id="the-canvas"></canvas>
                    <script>
                        const url = 'data:application/pdf;base64,{pdf_base64}';
                        var pdfjsLib = window['pdfjs-dist/build/pdf'];
                        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

                        var pdfDoc = null,
                            pageNum = 1,
                            pageRendering = false,
                            pageNumPending = null,
                            scale = 1.0,
                            canvas = document.getElementById('the-canvas'),
                            ctx = canvas.getContext('2d');

                        function renderPage(num) {{
                            pageRendering = true;
                            pdfDoc.getPage(num).then(function(page) {{
                                var viewport = page.getViewport({{scale: scale}});
                                // Calculate scale to fit width
                                var desiredWidth = window.innerWidth - 40;
                                var scaleRequired = desiredWidth / viewport.width;
                                viewport = page.getViewport({{scale: scaleRequired}});
                                
                                canvas.height = viewport.height;
                                canvas.width = viewport.width;

                                var renderContext = {{
                                    canvasContext: ctx,
                                    viewport: viewport
                                }};
                                var renderTask = page.render(renderContext);

                                renderTask.promise.then(function() {{
                                    pageRendering = false;
                                    if (pageNumPending !== null) {{
                                        renderPage(pageNumPending);
                                        pageNumPending = null;
                                    }}
                                }});
                            }});

                            document.getElementById('page_num').textContent = num;
                        }}

                        function queueRenderPage(num) {{
                            if (pageRendering) {{
                                pageNumPending = num;
                            }} else {{
                                renderPage(num);
                            }}
                        }}

                        function onPrevPage() {{
                            if (pageNum <= 1) {{
                                return;
                            }}
                            pageNum--;
                            queueRenderPage(pageNum);
                        }}
                        document.getElementById('prev').addEventListener('click', onPrevPage);

                        function onNextPage() {{
                            if (pageNum >= pdfDoc.numPages) {{
                                return;
                            }}
                            pageNum++;
                            queueRenderPage(pageNum);
                        }}
                        document.getElementById('next').addEventListener('click', onNextPage);

                        pdfjsLib.getDocument(url).promise.then(function(pdfDoc_) {{
                            pdfDoc = pdfDoc_;
                            document.getElementById('page_count').textContent = pdfDoc.numPages;
                            renderPage(pageNum);
                        }});
                    </script>
                </body>
                </html>
                """
                components.html(pdf_viewer_html, height=height, scrolling=True)
            else:
                st.warning(f"Could not load PDF (Status: {response.status_code})")
            
            # Always show download link as fallback
            st.markdown(f"[📥 Download PDF]({preview_url})")
            
        except Exception as e:
            st.error(f"Preview error: {str(e)[:100]}")
            st.markdown(f"[📥 Download PDF]({preview_url})")
        
    elif file_type == "docx":
        # DOCX: Download link
        st.info("📄 Word documents can be previewed after download")
        st.markdown(f"[📥 Download Document]({preview_url})")
            
    elif file_type in ["pptx", "ppt"]:
        # PPT: Download link 
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
