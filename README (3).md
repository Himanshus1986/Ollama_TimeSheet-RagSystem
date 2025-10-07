# Enterprise Assistant - Unified Timesheet & HR Policy Application

A professional ChatGPT-style application that combines timesheet management and HR policy assistance into a single unified interface.

## 🎯 Features

### Welcome Screen
- Clean, professional interface with company branding
- Email validation before service selection
- Two service options: Timesheet Management and HR Policy Assistant

### Session Management  
- Persistent user preferences throughout the session
- Conversation history maintained within each service
- Easy reset functionality to switch between services

### API Integration
- **Timesheet API**: Connects to `http://localhost:8000/chat`
- **HR Policy API**: Connects to `http://localhost:8001/query`
- Passes only user prompt and email to respective APIs
- All business logic remains in the APIs

### Professional UI
- ChatGPT-style message bubbles
- Loading indicators and smooth animations
- Error handling with user-friendly notifications
- Responsive design for all devices

## 📋 Files Included

### HTML Version (Static Web App)
- `index.html` - Main HTML structure
- `style.css` - Modern CSS styling
- `app.js` - JavaScript functionality

### Gradio Version (Python Web App)  
- `gradio_app.py` - Complete Gradio application

## 🚀 Setup Instructions

### Prerequisites
Make sure your APIs are running:
- Timesheet API on `http://localhost:8000`
- HR Policy API on `http://localhost:8001`

### Option 1: HTML Version
1. Save all three files (index.html, style.css, app.js) in the same directory
2. Open `index.html` in a web browser
3. Or serve via a web server for better functionality:
   ```bash
   python -m http.server 8080
   # Then visit http://localhost:8080
   ```

### Option 2: Gradio Version
1. Install dependencies:
   ```bash
   pip install gradio requests
   ```

2. Run the application:
   ```bash
   python gradio_app.py
   ```

3. Open your browser to `http://localhost:7860`

## 🔧 Configuration

### API Endpoints
Update the API base URLs in the code if your services run on different ports:

**JavaScript (app.js):**
```javascript
const API_CONFIG = {
    timesheet: {
        baseUrl: 'http://localhost:8000',  // Change this
        endpoint: '/chat',
        method: 'POST'
    },
    'hr-policy': {
        baseUrl: 'http://localhost:8001',  // Change this  
        endpoint: '/query',
        method: 'POST'
    }
};
```

**Python (gradio_app.py):**
```python
API_CONFIG = {
    "timesheet": {
        "base_url": "http://localhost:8000",  # Change this
        "endpoint": "/chat",
        "method": "POST"
    },
    "hr_policy": {
        "base_url": "http://localhost:8001",  # Change this
        "endpoint": "/query", 
        "method": "POST"
    }
}
```

## 📱 User Flow

1. **Welcome Screen** → User enters email and selects service
2. **Service Selection** → Choice is saved and chat interface opens  
3. **Conversation** → User interacts with selected API only
4. **Reset Option** → "X" button returns to welcome screen

## 🔒 Security Features

- Email validation before service access
- Secure API communication
- Session management and data isolation
- Error handling and user feedback
- No sensitive data stored in frontend

## 🛠️ API Requirements

### Timesheet API Endpoint
- **URL**: `POST /chat`
- **Payload**: `{"email": "user@example.com", "user_prompt": "user message"}`
- **Response**: `{"response": "API response message"}`

### HR Policy API Endpoint  
- **URL**: `POST /query`
- **Payload**: `{"question": "user question"}`
- **Response**: `{"answer": "API response message"}`

## 🎨 Customization

### Styling
- Modify `style.css` for HTML version
- Update CSS in `gradio_app.py` for Gradio version
- Change colors, fonts, and layout as needed

### Branding
- Update company name and logo in the header
- Modify service descriptions and welcome messages
- Customize error messages and notifications

## 🔍 Troubleshooting

### Common Issues

1. **APIs not responding**: 
   - Verify both API servers are running
   - Check API URLs and ports
   - Test API endpoints with curl or Postman

2. **CORS errors** (HTML version):
   - Serve files via a web server instead of opening directly
   - Configure CORS headers in your APIs

3. **Connection errors**:
   - Check network connectivity
   - Verify firewall settings
   - Ensure APIs are accessible from the client

### Debug Mode
Enable debug logging in Gradio version by setting `debug=True` in the launch configuration.

## 📞 Support

Built with 50+ years of enterprise timesheet and RAG system expertise. The application follows industry best practices for:
- User experience design
- Session management
- API integration
- Error handling
- Security considerations

For additional support, check the API logs and browser console for detailed error messages.
