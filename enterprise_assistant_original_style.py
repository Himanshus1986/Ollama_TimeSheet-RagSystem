"""
🤖 Enterprise Assistant - Auto Login with Original ChatGPT Style
✅ Auto Windows Username Detection  
✅ Centered Clickable Service Areas
✅ Original ChatGPT-style conversation bubbles and thinking messages
🚀 Professional Interface with 50+ Years Experience
"""

import gradio as gr
import requests
import json
import asyncio
import time
import os
import getpass
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🎯 API Configuration - Perfectly Aligned with Fixed APIs
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
    """Enhanced chat state management with ChatGPT-like features"""
    def __init__(self):
        self.selected_service = None
        # Auto-detect Windows username
        self.user_email = f"{getpass.getuser()}@company.com"  # Auto Windows username
        self.conversation_history = []
        self.is_initialized = False
        self.session_start = datetime.now()
        self.message_count = 0

    def reset(self):
        """Reset state for fresh conversation"""
        self.selected_service = None
        # Keep the auto-detected username
        self.user_email = f"{getpass.getuser()}@company.com"
        self.conversation_history = []
        self.is_initialized = False
        self.session_start = datetime.now()
        self.message_count = 0

def get_windows_username():
    """Get current Windows username"""
    try:
        return getpass.getuser()
    except Exception:
        return "user"

async def call_api(service: str, message: str, email: str = None) -> Dict[str, Any]:
    """Enhanced API calling with proper error handling"""
    try:
        config = API_CONFIG[service]
        url = f"{config['base_url']}{config['endpoint']}"

        # Prepare payload based on service type
        if service == "timesheet":
            payload = {
                "email": email,
                "user_prompt": message
            }
        else:  # hr_policy
            payload = {
                "question": message
            }

        logger.info(f"Calling {service} API: {url}")

        response = requests.post(
            url,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ {service} API responded successfully")

            # Handle different response formats
            if service == "timesheet":
                return {
                    "success": True,
                    "message": data.get("response", data.get("message", "Response received successfully.")),
                    "data": data.get("data", {})
                }
            else:  # hr_policy
                answer = data.get("answer", data.get("response", data.get("message", "Response received successfully.")))
                sources = data.get("sources", [])
                if sources:
                    answer += f"\n\n📚 **Sources:** {', '.join(sources)}"
                return {
                    "success": True,
                    "message": answer,
                    "data": {"sources": sources}
                }
        else:
            logger.error(f"❌ API Error: {response.status_code}")
            return {
                "success": False,
                "message": f"API Error ({response.status_code}): Please check if the service is running.",
                "data": {}
            }

    except requests.exceptions.ConnectionError:
        logger.error(f"❌ Connection error to {service} API")
        return {
            "success": False,
            "message": f"🔌 Cannot connect to {config['name']} service. Please ensure the API server is running on {config['base_url']}.",
            "data": {}
        }
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        return {
            "success": False,
            "message": f"❌ An unexpected error occurred: {str(e)}",
            "data": {}
        }

def format_chat_message_html(role: str, content: str, timestamp: str = None, service: str = None) -> str:
    """Format message with EXACT original ChatGPT-style appearance"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%I:%M %p")

    if role == "user":
        return f"""
<div style="display: flex; justify-content: flex-end; margin-bottom: 16px;">
    <div style="background: #0084ff; color: white; padding: 12px 16px; border-radius: 18px 18px 4px 18px; max-width: 70%; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; font-size: 15px; line-height: 1.4;">
        {content}
    </div>
</div>"""
    else:
        # Assistant message with original ChatGPT styling
        service_info = ""
        if service and service in API_CONFIG:
            config = API_CONFIG[service]
            service_info = f"""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid #e5e7eb;">
                <span style="font-size: 16px;">{config['icon']}</span>
                <span style="font-weight: 600; color: {config['color']}; font-size: 14px;">{config['name']}</span>
            </div>
            """

        return f"""
<div style="display: flex; justify-content: flex-start; margin-bottom: 16px;">
    <div style="background: #f7f7f8; color: #374151; padding: 16px; border-radius: 18px 18px 18px 4px; max-width: 70%; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; font-size: 15px; line-height: 1.5; border: 1px solid #e5e7eb;">
        {service_info}
        <div style="white-space: pre-wrap;">{content}</div>
    </div>
</div>"""

def create_original_typing_indicator() -> str:
    """Create original ChatGPT-style typing indicator"""
    return """
<div style="display: flex; justify-content: flex-start; margin-bottom: 16px;">
    <div style="background: #f7f7f8; padding: 16px; border-radius: 18px 18px 18px 4px; border: 1px solid #e5e7eb;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="display: flex; gap: 4px;">
                <div class="bounce-dot" style="width: 8px; height: 8px; border-radius: 50%; background: #9ca3af;"></div>
                <div class="bounce-dot" style="width: 8px; height: 8px; border-radius: 50%; background: #9ca3af; animation-delay: -0.16s;"></div>
                <div class="bounce-dot" style="width: 8px; height: 8px; border-radius: 50%; background: #9ca3af; animation-delay: 0s;"></div>
            </div>
            <span style="color: #6b7280; font-style: italic; font-size: 14px;">Assistant is typing...</span>
        </div>
    </div>
</div>
"""

def select_service(service: str, state: ChatState) -> Tuple[str, str, gr.update, gr.update, ChatState]:
    """Handle service selection directly with Windows username"""

    # Update state with auto-detected user
    state.selected_service = service
    state.is_initialized = True
    state.conversation_history = []

    # Get service configuration
    config = API_CONFIG[service]
    username = get_windows_username()

    # Create service welcome message
    service_welcome = f"""Hello **{username}**! I'm your **{config['name']}** assistant.

{config['description']}

I'm ready to help you with {config['name'].lower()}. What would you like to do today?

You can ask me questions, get help, or start working with your {config['name'].lower()}."""

    # Add to conversation history
    state.conversation_history.append({
        "role": "assistant",
        "content": service_welcome,
        "timestamp": datetime.now().strftime("%I:%M %p"),
        "service": service
    })

    # Format with original ChatGPT HTML styling
    chat_html = format_chat_message_html("assistant", service_welcome, service=service)

    return (
        chat_html,  # HTML formatted chat display
        "",  # message input (clear)
        gr.update(visible=False),  # hide service selection
        gr.update(visible=True),   # show chat interface
        state
    )

# FIXED: Async generator function with original ChatGPT-style HTML rendering
async def handle_message(message: str, state: ChatState):
    """Handle messages with original ChatGPT-style processing and HTML display"""

    if not message.strip() or not state.is_initialized:
        yield "", "", state
        return

    # Add user message to history
    timestamp = datetime.now().strftime("%I:%M %p")
    state.conversation_history.append({
        "role": "user", 
        "content": message,
        "timestamp": timestamp
    })
    state.message_count += 1

    # Build conversation HTML with user message (original style)
    messages_html = ""
    for msg in state.conversation_history:
        messages_html += format_chat_message_html(
            msg["role"], 
            msg["content"], 
            msg["timestamp"], 
            msg.get("service", state.selected_service)
        )

    # Add original typing indicator
    chat_with_typing = messages_html + create_original_typing_indicator()

    # Show typing state first (original ChatGPT style)
    yield chat_with_typing, "", state

    # Small delay for realistic typing effect
    await asyncio.sleep(1.2)

    try:
        # Call API
        api_result = await call_api(state.selected_service, message, state.user_email)

        if api_result["success"]:
            response = api_result["message"]
        else:
            response = api_result["message"]

    except Exception as e:
        response = f"I apologize, but I encountered an unexpected error: {str(e)}\n\nPlease try again or check if the service is running."

    # Add assistant response to history
    state.conversation_history.append({
        "role": "assistant",
        "content": response, 
        "timestamp": datetime.now().strftime("%I:%M %p"),
        "service": state.selected_service
    })

    # Create final chat display without typing indicator (original ChatGPT HTML style)
    final_messages_html = ""
    for msg in state.conversation_history:
        final_messages_html += format_chat_message_html(
            msg["role"],
            msg["content"], 
            msg["timestamp"],
            msg.get("service", state.selected_service)
        )

    yield final_messages_html, "", state

def reset_conversation(state: ChatState) -> Tuple[str, gr.update, gr.update, ChatState]:
    """Reset to service selection"""

    # Reset state but keep username
    state.reset()

    return (
        "",  # clear chat HTML
        gr.update(visible=True),   # show service selection
        gr.update(visible=False),  # hide chat interface
        state
    )

def create_service_selection_interface():
    """Create centered service selection interface"""

    username = get_windows_username()

    with gr.Column(elem_id="service-selection", elem_classes=["service-container"]):
        gr.Markdown(f"""
        # 🏢 Enterprise Assistant
        ### Welcome, **{username}**!

        Your AI-powered workspace companion is ready to help.
        Please select a service to get started:
        """, elem_classes=["welcome-header"])

        with gr.Row(elem_classes=["service-row"]):
            # Timesheet Management Card
            timesheet_btn = gr.Button(
                """
                ⏰ **Timesheet Management**

                Manage your Oracle and Mars timesheets with AI assistance
                """,
                elem_id="timesheet-service",
                elem_classes=["service-card", "timesheet-card"],
                size="lg"
            )

            # HR Policy Assistant Card  
            hr_policy_btn = gr.Button(
                """
                📋 **HR Policy Assistant**

                Get answers about company policies and HR documents
                """,
                elem_id="hr-policy-service", 
                elem_classes=["service-card", "hr-policy-card"],
                size="lg"
            )

        gr.Markdown("🔒 Your conversations are secure and private", 
                   elem_classes=["security-note"])

    return timesheet_btn, hr_policy_btn

# 🎨 Create the main ChatGPT-style interface with original conversation styling
def create_enterprise_interface():
    """Create the main enterprise ChatGPT-style interface with original HTML chat bubbles"""

    # Custom CSS for professional styling with original ChatGPT conversation style
    custom_css = """
    /* Enterprise ChatGPT Style - Original Conversation Bubbles */
    .gradio-container {
        max-width: 1000px !important;
        margin: 0 auto !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif !important;
    }

    .service-container {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 70vh !important;
        padding: 2rem !important;
    }

    .welcome-header {
        text-align: center !important;
        margin-bottom: 3rem !important;
    }

    .service-row {
        display: flex !important;
        gap: 2rem !important;
        justify-content: center !important;
        align-items: stretch !important;
        max-width: 800px !important;
        width: 100% !important;
    }

    .service-card {
        flex: 1 !important;
        min-height: 200px !important;
        padding: 2rem !important;
        border-radius: 16px !important;
        border: 2px solid #e1e5e9 !important;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        text-align: center !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        white-space: pre-line !important;
    }

    .service-card:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15) !important;
        border-color: #0066cc !important;
    }

    .timesheet-card:hover {
        border-color: #0066cc !important;
        background: linear-gradient(135deg, #e3f2fd 0%, #ffffff 100%) !important;
    }

    .hr-policy-card:hover {
        border-color: #7c3aed !important;
        background: linear-gradient(135deg, #f3e8ff 0%, #ffffff 100%) !important;
    }

    .security-note {
        text-align: center !important;
        color: #6b7280 !important;
        font-size: 0.9rem !important;
        margin-top: 2rem !important;
    }

    /* Original ChatGPT Chat Interface Styling */
    .chat-interface {
        min-height: 600px !important;
    }

    .chat-display {
        background: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 12px !important;
        min-height: 500px !important;
        max-height: 600px !important;
        overflow-y: auto !important;
        padding: 20px !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif !important;
    }

    .message-input {
        border: 1px solid #d1d5db !important;
        border-radius: 12px !important;
        font-size: 16px !important;
        padding: 12px 16px !important;
        resize: none !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif !important;
    }

    .message-input:focus {
        border-color: #0084ff !important;
        box-shadow: 0 0 0 3px rgba(0, 132, 255, 0.1) !important;
        outline: none !important;
    }

    .send-button, .reset-button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }

    .send-button {
        background: #0084ff !important;
        color: white !important;
        border: none !important;
    }

    .send-button:hover:not(:disabled) {
        background: #0066cc !important;
    }

    .send-button:disabled {
        background: #9ca3af !important;
        cursor: not-allowed !important;
    }

    .reset-button {
        background: #ef4444 !important;
        color: white !important;
        border: none !important;
    }

    .reset-button:hover {
        background: #dc2626 !important;
    }

    /* Original ChatGPT Typing Animation */
    .bounce-dot {
        animation: bounce 1.4s ease-in-out infinite both;
    }

    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .service-row {
            flex-direction: column !important;
            gap: 1rem !important;
        }

        .service-card {
            min-height: 150px !important;
            padding: 1.5rem !important;
        }

        .service-container {
            padding: 1rem !important;
            min-height: 60vh !important;
        }

        .chat-display {
            padding: 15px !important;
        }
    }
    """

    with gr.Blocks(
        title="🏢 Enterprise Assistant - Original ChatGPT Style",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="gray",
            neutral_hue="gray",
            font=gr.themes.GoogleFont("Inter")
        ),
        css=custom_css,
        fill_height=True
    ) as app:

        # Application state
        state = gr.State(ChatState())

        # Service Selection Interface (Visible by default)
        with gr.Group(visible=True) as service_selection:
            timesheet_btn, hr_policy_btn = create_service_selection_interface()

        # Chat Interface (Hidden by default) - Using HTML for original ChatGPT styling
        with gr.Group(visible=False, elem_classes=["chat-interface"]) as chat_interface:

            # Chat Display - HTML for original ChatGPT bubble styling
            chat_display = gr.HTML(
                "",
                elem_classes=["chat-display"]
            )

            # Input Area
            with gr.Row():
                with gr.Column(scale=5):
                    msg_input = gr.Textbox(
                        placeholder="Type your message here... (Press Enter to send)",
                        label="",
                        lines=1,
                        max_lines=4,
                        elem_classes=["message-input"],
                        show_label=False
                    )
                with gr.Column(scale=1):
                    send_btn = gr.Button(
                        "Send",
                        elem_classes=["send-button"]
                    )

            # Control Buttons
            with gr.Row():
                reset_btn = gr.Button(
                    "🔄 New Service Selection",
                    elem_classes=["reset-button"],
                    size="sm"
                )

                # Show current user info
                username = get_windows_username()
                gr.Markdown(f"**Logged in as:** {username}", elem_classes=["user-info"])

        # Event Handlers

        # Service Selection
        timesheet_btn.click(
            fn=lambda state: select_service("timesheet", state),
            inputs=[state],
            outputs=[chat_display, msg_input, service_selection, chat_interface, state]
        )

        hr_policy_btn.click(
            fn=lambda state: select_service("hr_policy", state),
            inputs=[state],
            outputs=[chat_display, msg_input, service_selection, chat_interface, state]
        )

        # Send Message with original ChatGPT-style streaming
        send_btn.click(
            fn=handle_message,
            inputs=[msg_input, state],
            outputs=[chat_display, msg_input, state],
            show_progress=False
        )

        # Enter Key Support
        msg_input.submit(
            fn=handle_message,
            inputs=[msg_input, state],
            outputs=[chat_display, msg_input, state],
            show_progress=False
        )

        # Reset to Service Selection
        reset_btn.click(
            fn=reset_conversation,
            inputs=[state],
            outputs=[chat_display, service_selection, chat_interface, state]
        )

        # Footer
        gr.Markdown("""
        ---
        <div style="text-align: center; color: #6b7280; font-size: 0.9rem;">
            🤖 Enterprise Assistant • ✅ Auto Windows Login • 💬 Original ChatGPT Style
        </div>
        """)

    return app

# 🚀 Launch the application
if __name__ == "__main__":
    print("🤖 Starting Enterprise Assistant with Original ChatGPT Style...")
    print(f"👤 Detected user: {get_windows_username()}")
    print("✨ Features:")
    print("   ✅ Auto Windows username detection")
    print("   🎯 Centered clickable service areas") 
    print("   💬 Original ChatGPT-style conversation bubbles")
    print("   🤔 Original thinking message animations")
    print("   🔌 API Integration: Timesheet (8000) + HR Policy (8001)")
    print("\n🌟 Professional interface with original ChatGPT conversation style!")

    # Create and launch the app
    app = create_enterprise_interface()

    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_api=False,
        show_error=True,
        debug=False,
        inbrowser=True,
        favicon_path=None
    )
