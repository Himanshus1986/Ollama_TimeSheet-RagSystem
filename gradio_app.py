"""
Unified Timesheet & HR Policy Assistant - Gradio Application
Combines timesheet management and HR policy RAG functionality
Built with 50+ years of timesheet and RAG system expertise
"""

import gradio as gr
import requests
import json
from typing import Optional, Tuple, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
API_CONFIG = {
    "timesheet": {
        "base_url": "http://localhost:8000",
        "endpoint": "/chat",
        "method": "POST"
    },
    "hr_policy": {
        "base_url": "http://localhost:8001", 
        "endpoint": "/query",
        "method": "POST"
    }
}

# Service Configuration
SERVICES = {
    "timesheet": {
        "name": "Timesheet Management",
        "description": "Manage your Oracle and Mars timesheets with AI assistance",
        "welcome": "Hello! I'm your Timesheet Management assistant. I can help you fill timesheets, view entries, and manage your Oracle and Mars timesheet data. How can I assist you today?"
    },
    "hr_policy": {
        "name": "HR Policy Assistant", 
        "description": "Get answers about company policies and HR documents",
        "welcome": "Hello! I'm your HR Policy Assistant. I can help you understand company policies, HR procedures, and answer questions about employee documentation. How can I help you today?"
    }
}

class ChatState:
    def __init__(self):
        self.selected_service = None
        self.user_email = ""
        self.conversation_history = []
        self.initialized = False

def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email)) if email else False

async def call_api(service: str, message: str, email: str = None) -> str:
    """Call the appropriate API based on selected service"""
    try:
        config = API_CONFIG[service]
        url = f"{config['base_url']}{config['endpoint']}"

        # Prepare payload based on service
        if service == "timesheet":
            payload = {
                "email": email,
                "user_prompt": message
            }
        else:  # hr_policy
            payload = {
                "question": message
            }

        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            # Handle different response formats
            if service == "timesheet":
                return data.get("response", data.get("message", "Response received successfully."))
            else:  # hr_policy
                return data.get("answer", data.get("response", data.get("message", "Response received successfully.")))
        else:
            logger.error(f"API Error: {response.status_code} - {response.text}")
            return f"Sorry, I encountered an error (Status: {response.status_code}). Please try again."

    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error to {service} API")
        return f"Unable to connect to {SERVICES[service]['name']} service. Please ensure the API server is running."
    except requests.exceptions.Timeout:
        logger.error(f"Timeout error for {service} API")
        return "Request timed out. Please try again."
    except Exception as e:
        logger.error(f"Unexpected error calling {service} API: {str(e)}")
        return f"An unexpected error occurred: {str(e)}"

def select_service(service: str, email: str, state: ChatState) -> Tuple[str, str, str, gr.update, gr.update, gr.update, ChatState]:
    """Handle service selection"""

    # Validate email
    if not email or not validate_email(email):
        return (
            gr.update(),  # chat_interface
            gr.update(),  # welcome_screen  
            "❌ Please enter a valid email address.",  # status_message
            gr.update(),  # chat_display
            gr.update(),  # msg_input
            gr.update(),  # send_btn
            state
        )

    # Update state
    state.selected_service = service
    state.user_email = email
    state.conversation_history = []
    state.initialized = True

    # Get service info
    service_info = SERVICES[service]
    welcome_msg = service_info["welcome"]

    # Create initial chat display
    chat_html = f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin-bottom: 10px;">
        <h3 style="color: white; margin: 0; display: flex; align-items: center;">
            <span style="margin-right: 10px;">{'⏰' if service == 'timesheet' else '📋'}</span>
            {service_info['name']}
        </h3>
        <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 14px;">
            Connected as: {email}
        </p>
    </div>
    <div style="background: #f1f3f4; padding: 15px; border-radius: 10px; margin: 10px 0;">
        <strong>Assistant:</strong> {welcome_msg}
    </div>
    """

    return (
        gr.update(visible=True),   # chat_interface
        gr.update(visible=False),  # welcome_screen
        f"✅ Connected to {service_info['name']}",  # status_message
        chat_html,  # chat_display
        gr.update(placeholder="Type your message here...", interactive=True),  # msg_input
        gr.update(interactive=True),  # send_btn
        state
    )

async def send_message(message: str, state: ChatState) -> Tuple[str, str, str, ChatState]:
    """Handle sending messages"""

    if not message.strip():
        return (
            gr.update(),  # chat_display
            "",           # msg_input (clear)
            "Please enter a message.",  # status_message
            state
        )

    if not state.initialized or not state.selected_service:
        return (
            gr.update(),  # chat_display
            message,      # msg_input (keep message)
            "❌ Please select a service first.",  # status_message
            state
        )

    # Add user message to history
    state.conversation_history.append({"role": "user", "content": message})

    # Update chat display with user message
    service_info = SERVICES[state.selected_service]
    chat_html = f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin-bottom: 10px;">
        <h3 style="color: white; margin: 0; display: flex; align-items: center;">
            <span style="margin-right: 10px;">{'⏰' if state.selected_service == 'timesheet' else '📋'}</span>
            {service_info['name']}
        </h3>
        <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 14px;">
            Connected as: {state.user_email}
        </p>
    </div>
    """

    # Add conversation history
    for msg in state.conversation_history:
        if msg["role"] == "user":
            chat_html += f"""
            <div style="background: #0066cc; color: white; padding: 12px 15px; border-radius: 15px; margin: 10px 0; margin-left: 50px; text-align: right;">
                <strong>You:</strong> {msg["content"]}
            </div>
            """

    # Show typing indicator
    chat_html += """
    <div style="background: #f1f3f4; padding: 15px; border-radius: 10px; margin: 10px 0; margin-right: 50px;">
        <strong>Assistant:</strong> <em>Typing...</em>
    </div>
    """

    # Call API
    try:
        response = await call_api(state.selected_service, message, state.user_email)
    except Exception as e:
        response = f"Error: {str(e)}"

    # Add assistant response to history
    state.conversation_history.append({"role": "assistant", "content": response})

    # Update chat display with response
    chat_html = f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin-bottom: 10px;">
        <h3 style="color: white; margin: 0; display: flex; align-items: center;">
            <span style="margin-right: 10px;">{'⏰' if state.selected_service == 'timesheet' else '📋'}</span>
            {service_info['name']}
        </h3>
        <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 14px;">
            Connected as: {state.user_email}
        </p>
    </div>
    """

    # Add full conversation history
    for msg in state.conversation_history:
        if msg["role"] == "user":
            chat_html += f"""
            <div style="background: #0066cc; color: white; padding: 12px 15px; border-radius: 15px; margin: 10px 0; margin-left: 50px; text-align: right;">
                <strong>You:</strong> {msg["content"]}
            </div>
            """
        else:
            chat_html += f"""
            <div style="background: #f1f3f4; padding: 15px; border-radius: 10px; margin: 10px 0; margin-right: 50px;">
                <strong>Assistant:</strong> {msg["content"]}
            </div>
            """

    return (
        chat_html,  # chat_display
        "",         # msg_input (clear)
        f"✅ Message sent to {service_info['name']}",  # status_message
        state
    )

def reset_application(state: ChatState) -> Tuple[gr.update, gr.update, str, str, str, gr.update, gr.update, ChatState]:
    """Reset application to welcome screen"""

    # Reset state
    state.selected_service = None
    state.user_email = ""
    state.conversation_history = []
    state.initialized = False

    return (
        gr.update(visible=False),  # chat_interface
        gr.update(visible=True),   # welcome_screen
        "",                        # status_message
        "",                        # email_input
        "",                        # chat_display
        gr.update(placeholder="Type your message here...", interactive=False),  # msg_input
        gr.update(interactive=False),  # send_btn
        state
    )

# Create Gradio Interface
def create_interface():
    with gr.Blocks(
        title="Enterprise Assistant - Timesheet & HR Policy",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .welcome-header {
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            margin-bottom: 25px;
            color: white;
        }
        .service-btn {
            padding: 20px !important;
            margin: 10px !important;
            border-radius: 10px !important;
            border: 2px solid #e0e0e0 !important;
        }
        .service-btn:hover {
            border-color: #667eea !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3) !important;
        }
        """
    ) as app:

        # Application State
        state = gr.State(ChatState())

        gr.Markdown("""
        <div class="welcome-header">
            <h1>🏢 Enterprise Assistant</h1>
            <p style="font-size: 18px; margin: 10px 0;">Your AI-powered workspace companion</p>
        </div>
        """)

        # Status message
        status_message = gr.Markdown("", visible=True)

        with gr.Group() as welcome_screen:
            gr.Markdown("## Welcome! Please choose your preferred service:")

            email_input = gr.Textbox(
                label="📧 Email Address",
                placeholder="Enter your email address",
                type="email"
            )

            with gr.Row():
                with gr.Column():
                    gr.Markdown("### ⏰ Timesheet Management")
                    gr.Markdown("Manage your Oracle and Mars timesheets with AI assistance")
                    timesheet_btn = gr.Button(
                        "Select Timesheet Service",
                        variant="primary",
                        elem_classes=["service-btn"]
                    )

                with gr.Column():
                    gr.Markdown("### 📋 HR Policy Assistant")
                    gr.Markdown("Get answers about company policies and HR documents")
                    hr_policy_btn = gr.Button(
                        "Select HR Policy Service", 
                        variant="primary",
                        elem_classes=["service-btn"]
                    )

        with gr.Group(visible=False) as chat_interface:
            with gr.Row():
                with gr.Column(scale=4):
                    chat_display = gr.HTML(label="Conversation")
                with gr.Column(scale=1):
                    reset_btn = gr.Button("🔄 New Conversation", variant="secondary")

            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Please select a service first...",
                    label="Your Message",
                    interactive=False,
                    lines=2
                )
                send_btn = gr.Button("Send 📤", interactive=False)

        # Event handlers
        timesheet_btn.click(
            fn=select_service,
            inputs=[gr.State("timesheet"), email_input, state],
            outputs=[chat_interface, welcome_screen, status_message, chat_display, msg_input, send_btn, state]
        )

        hr_policy_btn.click(
            fn=select_service,
            inputs=[gr.State("hr_policy"), email_input, state],
            outputs=[chat_interface, welcome_screen, status_message, chat_display, msg_input, send_btn, state]
        )

        send_btn.click(
            fn=send_message,
            inputs=[msg_input, state],
            outputs=[chat_display, msg_input, status_message, state]
        )

        msg_input.submit(
            fn=send_message,
            inputs=[msg_input, state],
            outputs=[chat_display, msg_input, status_message, state]
        )

        reset_btn.click(
            fn=reset_application,
            inputs=[state],
            outputs=[chat_interface, welcome_screen, status_message, email_input, chat_display, msg_input, send_btn, state]
        )

    return app

if __name__ == "__main__":
    # Create and launch the application
    app = create_interface()

    print("🚀 Starting Enterprise Assistant Application...")
    print("📋 Services Available:")
    print("   - Timesheet Management (http://localhost:8000)")
    print("   - HR Policy Assistant (http://localhost:8001)")
    print("\n⚠️  Make sure both API servers are running!")

    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_api=False,
        show_error=True,
        debug=True
    )
