```python
"""
🤖 Enterprise Assistant - ChatGPT Style Gradio Application
🎯 ChatGPT-like Interface with Timesheet & HR Policy Selection as First Message
"""

import gradio as gr
import requests
import json
import asyncio
import time
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🎯 API Configuration
API_CONFIG = {
    "timesheet": {
        "base_url": "http://localhost:8000",
        "endpoint": "/chat",
        "method": "POST",
        "name": "Timesheet Management",
        "description": "Manage your Oracle and Mars timesheets with AI assistance",
        "icon": "⏰",
        "color": "#0066cc"
    },
    "hr_policy": {
        "base_url": "http://localhost:8001", 
        "endpoint": "/query",
        "method": "POST",
        "name": "HR Policy Assistant",
        "description": "Get answers about company policies and HR documents", 
        "icon": "📋",
        "color": "#7c3aed"
    }
}

class ChatState:
    def __init__(self):
        self.selected_service = None
        self.user_email = ""
        self.conversation_history = []
        self.is_initialized = True  # Start initialized with welcome msg
        self.session_start = datetime.now()
        self.message_count = 0

    def reset(self):
        self.selected_service = None
        self.user_email = ""
        self.conversation_history = []
        self.is_initialized = True
        self.session_start = datetime.now()
        self.message_count = 0

# Initial assistant welcome message inside chat
def initial_welcome_message():
    msg = """
👋 Hello! Welcome to the Enterprise Assistant.  
Please choose a service to get started:

- ⏰ **Timesheet Management** – Manage Oracle and Mars timesheets  
- 📋 **HR Policy Assistant** – Ask questions about policies and HR docs  

Please also provide your 📧 email address before starting.
"""
    return {
        "role": "assistant",
        "content": msg,
        "timestamp": datetime.now().strftime("%I:%M %p"),
        "service": None
    }

def format_chat_message(role: str, content: str, timestamp: str = None, service: str = None) -> str:
    if timestamp is None:
        timestamp = datetime.now().strftime("%I:%M %p")

    if role == "user":
        return f"""
<div style="display: flex; justify-content: flex-end; margin: 15px 0;">
    <div style="background: linear-gradient(135deg, #0066cc, #004499); color: white; padding: 12px 16px; border-radius: 18px 18px 4px 18px; max-width: 80%;">
        <div style="font-weight: 500; margin-bottom: 4px;">You</div>
        <div style="line-height: 1.5;">{content}</div>
        <div style="font-size: 11px; opacity: 0.8; margin-top: 8px; text-align: right;">{timestamp}</div>
    </div>
</div>"""
    else:
        return f"""
<div style="display: flex; justify-content: flex-start; margin: 15px 0;">
    <div style="background: #f8f9fa; color: #333; padding: 12px 16px; border-radius: 18px 18px 18px 4px; max-width: 80%; border-left: 4px solid #7c3aed;">
        <div style="font-weight: 600; margin-bottom: 8px; color: #7c3aed;">
            🤖 Assistant
        </div>
        <div style="line-height: 1.6; white-space: pre-wrap;">{content}</div>
        <div style="font-size: 11px; color: #666; margin-top: 8px;">{timestamp}</div>
    </div>
</div>"""

# Reset conversation
def reset_conversation(state: ChatState):
    state.reset()
    state.conversation_history.append(initial_welcome_message())
    msgs = "".join([
        format_chat_message(m["role"], m["content"], m["timestamp"]) for m in state.conversation_history
    ])
    return (
        msgs,
        "",
        gr.update(value="Welcome! Please select Timesheet or HR Policy to continue.", visible=True),
        state
    )

# Gradio UI
def create_chatgpt_interface():
    custom_css = """
    .gradio-container { max-width: 900px; margin: auto; }
    """

    with gr.Blocks(css=custom_css) as app:
        state = gr.State(ChatState())
        state.value.conversation_history.append(initial_welcome_message())

        chat_display = gr.HTML()
        msg_input = gr.Textbox(label="Your Message", placeholder="Type here...", lines=2)
        send_btn = gr.Button("Send 🚀")
        reset_btn = gr.Button("❌ New Conversation")
        status_display = gr.Markdown("Welcome! Please select Timesheet or HR Policy.")

        def render_chat(state: ChatState):
            msgs = "".join([
                format_chat_message(m["role"], m["content"], m["timestamp"]) for m in state.conversation_history
            ])
            return msgs

        chat_display.update(render_chat(state.value))

        def on_send(message, state: ChatState):
            if not message.strip():
                return render_chat(state), "", gr.update(value="Please enter a message", visible=True), state
            state.conversation_history.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().strftime("%I:%M %p")
            })
            return render_chat(state), "", gr.update(value="Message sent", visible=True), state

        send_btn.click(on_send, [msg_input, state], [chat_display, msg_input, status_display, state])
        msg_input.submit(on_send, [msg_input, state], [chat_display, msg_input, status_display, state])
        reset_btn.click(reset_conversation, [state], [chat_display, msg_input, status_display, state])

    return app

if __name__ == "__main__":
    app = create_chatgpt_interface()
    app.launch(server_name="0.0.0.0", server_port=7860, inbrowser=True)
```
