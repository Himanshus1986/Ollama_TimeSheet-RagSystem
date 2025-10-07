// Application State
let appState = {
    selectedService: null,
    userEmail: '',
    conversationHistory: [],
    isLoading: false
};

// API Configuration
const API_CONFIG = {
    timesheet: {
        baseUrl: 'http://localhost:8000',
        endpoint: '/chat',
        method: 'POST'
    },
    'hr-policy': {
        baseUrl: 'http://localhost:8001',
        endpoint: '/query',
        method: 'POST'
    }
};

// Service Configuration
const SERVICES = {
    timesheet: {
        name: 'Timesheet Management',
        description: 'your Oracle and Mars timesheets',
        api: 'timesheet'
    },
    'hr-policy': {
        name: 'HR Policy Assistant',
        description: 'HR policies and company documents',
        api: 'hr-policy'
    }
};

// DOM Elements
const elements = {
    welcomeScreen: document.getElementById('welcome-screen'),
    chatInterface: document.getElementById('chat-interface'),
    emailInput: document.getElementById('user-email'),
    emailError: document.getElementById('email-error'),
    timesheetBtn: document.getElementById('timesheet-btn'),
    hrPolicyBtn: document.getElementById('hr-policy-btn'),
    resetBtn: document.getElementById('reset-btn'),
    serviceName: document.getElementById('service-name'),
    serviceContext: document.getElementById('service-context'),
    userEmailDisplay: document.getElementById('user-email-display'),
    chatMessages: document.getElementById('chat-messages'),
    chatInput: document.getElementById('chat-input'),
    sendBtn: document.getElementById('send-btn'),
    loadingIndicator: document.getElementById('loading-indicator'),
    errorToast: document.getElementById('error-toast'),
    errorMessage: document.getElementById('error-message'),
    errorClose: document.getElementById('error-close')
};

// Initialize Application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    resetApplication();
});

function initializeEventListeners() {
    // Email input validation
    elements.emailInput.addEventListener('input', validateEmail);
    elements.emailInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (validateEmail()) {
                // Focus on first service button
                elements.timesheetBtn.focus();
            }
        }
    });

    // Service selection buttons
    elements.timesheetBtn.addEventListener('click', () => selectService('timesheet'));
    elements.hrPolicyBtn.addEventListener('click', () => selectService('hr-policy'));

    // Reset button
    elements.resetBtn.addEventListener('click', resetApplication);

    // Chat input handling
    elements.chatInput.addEventListener('input', function() {
        adjustTextareaHeight(this);
        toggleSendButton();
    });

    elements.chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Send button
    elements.sendBtn.addEventListener('click', sendMessage);

    // Error toast close
    elements.errorClose.addEventListener('click', hideErrorToast);
}

function validateEmail() {
    const email = elements.emailInput.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const isValid = emailRegex.test(email);

    if (!isValid && email.length > 0) {
        elements.emailError.classList.remove('hidden');
        elements.timesheetBtn.disabled = true;
        elements.hrPolicyBtn.disabled = true;
    } else {
        elements.emailError.classList.add('hidden');
        elements.timesheetBtn.disabled = !isValid;
        elements.hrPolicyBtn.disabled = !isValid;
    }

    return isValid;
}

function selectService(serviceType) {
    const email = elements.emailInput.value.trim();
    if (!validateEmail() || !email) {
        showError('Please enter a valid email address first.');
        elements.emailInput.focus();
        return;
    }

    // Save user preferences
    appState.selectedService = serviceType;
    appState.userEmail = email;
    appState.conversationHistory = [];

    // Update UI
    const service = SERVICES[serviceType];
    elements.serviceName.textContent = service.name;
    elements.serviceContext.textContent = service.description;
    elements.userEmailDisplay.textContent = email;

    // Switch to chat interface
    elements.welcomeScreen.classList.add('hidden');
    elements.chatInterface.classList.remove('hidden');

    // Focus on chat input
    elements.chatInput.focus();

    // Add welcome message
    addMessage('assistant', `Hello! I'm your ${service.name} assistant. How can I help you today?`);
}

function resetApplication() {
    // Reset state
    appState.selectedService = null;
    appState.userEmail = '';
    appState.conversationHistory = [];
    appState.isLoading = false;

    // Reset UI
    elements.emailInput.value = '';
    elements.emailError.classList.add('hidden');
    elements.timesheetBtn.disabled = true;
    elements.hrPolicyBtn.disabled = true;
    elements.chatMessages.innerHTML = '';
    elements.chatInput.value = '';
    elements.loadingIndicator.classList.add('hidden');
    hideErrorToast();

    // Show welcome screen
    elements.welcomeScreen.classList.remove('hidden');
    elements.chatInterface.classList.add('hidden');

    // Focus on email input
    elements.emailInput.focus();
}

function adjustTextareaHeight(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function toggleSendButton() {
    const hasText = elements.chatInput.value.trim().length > 0;
    elements.sendBtn.disabled = !hasText || appState.isLoading;
}

async function sendMessage() {
    const message = elements.chatInput.value.trim();
    if (!message || appState.isLoading) return;

    // Clear input and add user message
    elements.chatInput.value = '';
    adjustTextareaHeight(elements.chatInput);
    toggleSendButton();

    addMessage('user', message);
    showLoading(true);

    try {
        // Call appropriate API
        const response = await callAPI(message);
        addMessage('assistant', response);

        // Store in conversation history
        appState.conversationHistory.push(
            { role: 'user', content: message },
            { role: 'assistant', content: response }
        );
    } catch (error) {
        console.error('API Error:', error);
        showError('Sorry, I encountered an error. Please try again.');
        addMessage('assistant', 'I apologize, but I encountered an error processing your request. Please try again.');
    } finally {
        showLoading(false);
    }
}

async function callAPI(message) {
    const serviceConfig = API_CONFIG[appState.selectedService];

    let payload;
    if (appState.selectedService === 'timesheet') {
        payload = {
            email: appState.userEmail,
            user_prompt: message
        };
    } else if (appState.selectedService === 'hr-policy') {
        payload = {
            question: message
        };
    }

    const response = await fetch(`${serviceConfig.baseUrl}${serviceConfig.endpoint}`, {
        method: serviceConfig.method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // Handle different response formats
    if (appState.selectedService === 'timesheet') {
        return data.response || data.message || 'Response received successfully.';
    } else if (appState.selectedService === 'hr-policy') {
        return data.answer || data.response || data.message || 'Response received successfully.';
    }

    return 'Response received successfully.';
}

function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? 'U' : 'A';

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);

    elements.chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

function showLoading(show) {
    appState.isLoading = show;
    elements.loadingIndicator.classList.toggle('hidden', !show);
    elements.sendBtn.disabled = show || elements.chatInput.value.trim().length === 0;

    if (show) {
        // Scroll to show loading indicator
        elements.loadingIndicator.scrollIntoView({ behavior: 'smooth' });
    }
}

function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorToast.classList.remove('hidden');

    // Auto hide after 5 seconds
    setTimeout(() => {
        hideErrorToast();
    }, 5000);
}

function hideErrorToast() {
    elements.errorToast.classList.add('hidden');
}

// Handle window resize for mobile
window.addEventListener('resize', function() {
    if (elements.chatInput.value) {
        adjustTextareaHeight(elements.chatInput);
    }
});

// Handle network errors
window.addEventListener('online', function() {
    hideErrorToast();
});

window.addEventListener('offline', function() {
    showError('You are currently offline. Please check your internet connection.');
});