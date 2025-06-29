// Main chat functionality

// DOM Elements
const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const clearBtn = document.getElementById('clear-btn');
const themeToggle = document.getElementById('theme-toggle');

// Templates
const userMessageTemplate = document.getElementById('user-message-template');
const assistantMessageTemplate = document.getElementById('assistant-message-template');
const thinkingTemplate = document.getElementById('thinking-template');

// State
let isProcessing = false;
const darkModePreference = localStorage.getItem('darkMode') === 'true';
if (darkModePreference) {
    document.body.classList.add('dark-theme');
    themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
}

// Initialize chat with greeting
window.addEventListener('DOMContentLoaded', () => {
    fetchGreeting();
});

// Event Listeners
chatForm.addEventListener('submit', handleFormSubmit);
clearBtn.addEventListener('click', clearConversation);
themeToggle.addEventListener('click', toggleTheme);

// Functions
async function fetchGreeting() {
    try {
        const response = await fetch('/api/greeting');
        const data = await response.json();
        
        if (data.greeting) {
            addMessage('assistant', data.greeting);
        }
    } catch (error) {
        console.error('Error fetching greeting:', error);
        addMessage('assistant', 'Hello! How can I help you today?');
    }
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
}

function addMessage(role, text, timestamp = new Date().toISOString()) {
    const template = role === 'user' ? userMessageTemplate : assistantMessageTemplate;
    const messageElement = document.importNode(template.content, true);
    
    messageElement.querySelector('.message-text').textContent = text;
    messageElement.querySelector('.message-time').textContent = formatTimestamp(timestamp);
    
    chatMessages.appendChild(messageElement);
    scrollToBottom();
}

function addThinkingIndicator() {
    const thinkingElement = document.importNode(thinkingTemplate.content, true);
    chatMessages.appendChild(thinkingElement);
    scrollToBottom();
    return chatMessages.lastElementChild;
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function handleFormSubmit(event) {
    event.preventDefault();
    
    const message = userInput.value.trim();
    if (!message || isProcessing) return;
    
    // Add user message to chat
    addMessage('user', message);
    
    // Clear input
    userInput.value = '';
    
    // Set processing state
    isProcessing = true;
    userInput.disabled = true;
    
    // Add thinking indicator
    const thinkingIndicator = addThinkingIndicator();
    
    try {
        // Send message to API
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        // Remove thinking indicator
        thinkingIndicator.remove();
        
        if (data.response) {
            // Add assistant response
            addMessage('assistant', data.response, data.timestamp);
        } else {
            throw new Error('No response received');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        
        // Remove thinking indicator
        thinkingIndicator.remove();
        
        // Add error message
        addMessage('assistant', 'Sorry, I encountered an error processing your request. Please try again.');
    } finally {
        // Reset processing state
        isProcessing = false;
        userInput.disabled = false;
        userInput.focus();
    }
}

async function clearConversation() {
    if (confirm('Are you sure you want to clear the conversation history?')) {
        try {
            const response = await fetch('/api/clear', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                // Clear chat messages
                chatMessages.innerHTML = '';
                // Fetch new greeting
                fetchGreeting();
            }
        } catch (error) {
            console.error('Error clearing conversation:', error);
        }
    }
}

function toggleTheme() {
    const isDarkMode = document.body.classList.toggle('dark-theme');
    localStorage.setItem('darkMode', isDarkMode);
    
    // Update icon
    if (isDarkMode) {
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    } else {
        themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    }
}

// Handle pressing Enter to submit
userInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

