import gradio as gr
import requests
import json
import os
from typing import List

# Configuration
API_URL = "http://localhost:8000"

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=15, verify=False,)
        if response.status_code == 200:
            return True, "API is healthy and connected to Ollama"
        else:
            return False, f"API returned status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Cannot connect to API: {str(e)}"

def upload_files(files):
    """Upload PDF files to the API"""
    if not files:
        return "No files selected."
    
    try:
        # Prepare files for upload
        files_payload = []
        for file in files:
            files_payload.append(
                ("files", (os.path.basename(file.name), open(file.name, "rb"), "application/pdf"))
            )
        
        # Send files to API
        response = requests.post(f"{API_URL}/upload_pdfs", files=files_payload, timeout=60)
        
        # Close file handles
        for _, (_, file_handle, _) in files_payload:
            file_handle.close()
        
        if response.status_code == 200:
            result = response.json()
            return f"✅ Success: {result['message']}\nProcessed files: {', '.join(result['files'])}"
        else:
            error_msg = response.json().get('detail', 'Unknown error')
            return f"❌ Error: {error_msg}"
            
    except requests.exceptions.RequestException as e:
        return f"❌ Network Error: {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def ask_question(question, history):
    """Ask a question about the uploaded PDFs"""
    if not question.strip():
        return history, ""
    
    try:
        # Send query to API
        response = requests.post(
            f"{API_URL}/query", 
            json={"question": question},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result['answer']
            sources = result.get('sources', [])
            
            # Format response with sources
            if sources:
                formatted_answer = f"{answer}\n\n**Sources:**\n" + "\n".join([f"• {source}" for source in sources])
            else:
                formatted_answer = answer
            
            # Add to chat history
            history.append([question, formatted_answer])
            return history, ""
        else:
            error_msg = response.json().get('detail', 'Unknown error')
            history.append([question, f"❌ Error: {error_msg}"])
            return history, ""
            
    except requests.exceptions.RequestException as e:
        history.append([question, f"❌ Network Error: {str(e)}"])
        return history, ""
    except Exception as e:
        history.append([question, f"❌ Error: {str(e)}"])
        return history, ""

def clear_database():
    """Clear the vector database and uploaded files"""
    try:
        response = requests.delete(f"{API_URL}/clear_database", timeout=10)
        if response.status_code == 200:
            result = response.json()
            return f"✅ {result['message']}"
        else:
            error_msg = response.json().get('detail', 'Unknown error')
            return f"❌ Error: {error_msg}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Custom CSS for better styling
css = """
.container {
    max-width: 1200px;
    margin: 0 auto;
}
.upload-area {
    border: 2px dashed #ccc;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
}
.status-box {
    padding: 10px;
    border-radius: 5px;
    margin: 10px 0;
}
.success {
    background-color: #d4edda;
    border-color: #c3e6cb;
    color: #155724;
}
.error {
    background-color: #f8d7da;
    border-color: #f5c6cb;
    color: #721c24;
}
"""

# Create Gradio interface
with gr.Blocks(css=css, title="PDF Query System with Ollama") as demo:
    gr.Markdown(
        """
        # 📄 PDF Query System with Ollama
        
        Upload your PDF files and ask questions about their content using a local AI model.
        This system uses Ollama with Llama 3.2 1B model running entirely on your local machine.
        """
    )
    
    # API Health Check
    with gr.Row():
        with gr.Column():
            health_status = gr.Textbox(
                label="🔧 API Status", 
                interactive=False,
                placeholder="Checking API status..."
            )
            check_health_btn = gr.Button("🔄 Check API Health", variant="secondary")
    
    gr.Markdown("---")
    
    # File Upload Section
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📁 Upload PDF Files")
            pdf_uploader = gr.File(
                file_types=[".pdf"], 
                file_count="multiple", 
                label="Select PDF files to upload",
                height=100
            )
            upload_btn = gr.Button("📤 Upload and Process PDFs", variant="primary")
            upload_status = gr.Textbox(
                label="Upload Status", 
                interactive=False,
                lines=3
            )
    
    gr.Markdown("---")
    
    # Chat Interface Section
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 💬 Ask Questions About Your PDFs")
            chatbot = gr.Chatbot(
                label="Q&A Chat",
                height=400,
                placeholder="Upload PDFs first, then ask questions about their content..."
            )
            
            with gr.Row():
                question_input = gr.Textbox(
                    label="Your Question",
                    placeholder="Ask anything about the uploaded PDFs...",
                    lines=2,
                    scale=4
                )
                ask_btn = gr.Button("🚀 Ask", variant="primary", scale=1)
    
    gr.Markdown("---")
    
    # Database Management Section
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 🗑️ Database Management")
            clear_btn = gr.Button("🗑️ Clear All Data", variant="stop")
            clear_status = gr.Textbox(
                label="Clear Status", 
                interactive=False
            )
    
    # Event handlers
    def update_health_status():
        is_healthy, message = check_api_health()
        return f"{'✅' if is_healthy else '❌'} {message}"
    
    # Load health status on page load
    demo.load(update_health_status, outputs=health_status)
    
    # Button click events
    check_health_btn.click(update_health_status, outputs=health_status)
    upload_btn.click(upload_files, inputs=pdf_uploader, outputs=upload_status)
    ask_btn.click(ask_question, inputs=[question_input, chatbot], outputs=[chatbot, question_input])
    question_input.submit(ask_question, inputs=[question_input, chatbot], outputs=[chatbot, question_input])
    clear_btn.click(clear_database, outputs=clear_status)
    
    gr.Markdown(
        """
        ---
        ### ℹ️ Instructions:
        1. **Start the API server first** (see README.md for setup instructions)
        2. **Upload PDF files** using the file uploader above
        3. **Wait for processing** to complete (check upload status)
        4. **Ask questions** about the content of your PDFs
        5. **View answers** with source references in the chat interface
        
        ### 🔧 Requirements:
        - Ollama must be installed and running
        - Required models: `llama3.2:1b` and `nomic-embed-text`
        - API server must be running on `http://localhost:8000`
        """
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        debug=True
    )