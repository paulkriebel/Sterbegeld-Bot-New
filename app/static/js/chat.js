/**
 * Chat Interface JavaScript
 * Handles message sending, UI updates, and debug panel
 */

// Global state
let conversationHistory = [];

// DOM Elements
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const chatContainer = document.getElementById('chat-container');
const typingIndicator = document.getElementById('typing-indicator');
const debugToggle = document.getElementById('toggle-debug');
const debugContent = document.getElementById('debug-content');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Add welcome message
    addMessageToChat('bot', 'Hallo! Ich bin Sophie, Ihre Beraterin für Sterbegeldversicherungen. Wie kann ich Ihnen heute helfen?');
    
    // Setup event listeners
    chatForm.addEventListener('submit', handleSubmit);
    userInput.addEventListener('input', handleInput);
    debugToggle.addEventListener('click', toggleDebug);
    
    // Auto-resize textarea
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
    
    // Enable enter to send (shift+enter for newline)
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
});

/**
 * Handle form submission
 */
async function handleSubmit(e) {
    e.preventDefault();
    
    const message = userInput.value.trim();
    if (!message) return;
    
    // Disable input
    userInput.disabled = true;
    sendBtn.disabled = true;
    
    // Add user message to UI
    addMessageToChat('user', message);
    
    // Clear input
    userInput.value = '';
    userInput.style.height = 'auto';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send to API
    try {
        const response = await sendMessage(message);
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Add bot response
        addMessageToChat('bot', response.reply);
        
        // Update debug panel
        updateDebugPanel(response.debug);
        
    } catch (error) {
        hideTypingIndicator();
        addMessageToChat('bot', 'Entschuldigung, es gab einen Fehler. Bitte versuche es erneut.');
        console.error('Chat error:', error);
    }
    
    // Re-enable input
    userInput.disabled = false;
    sendBtn.disabled = false;
    userInput.focus();
}

/**
 * Send message to API
 */
async function sendMessage(message) {
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            conversation_history: conversationHistory
        })
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Update conversation history
    conversationHistory.push({ role: 'user', content: message });
    conversationHistory.push({ role: 'assistant', content: data.reply });
    
    // Keep only last 20 messages
    if (conversationHistory.length > 20) {
        conversationHistory = conversationHistory.slice(-20);
    }
    
    return data;
}

/**
 * Add message to chat UI with HTML formatting support
 */
function addMessageToChat(role, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Convert markdown-like formatting to HTML
    const formattedText = formatMessageText(text);
    contentDiv.innerHTML = formattedText;
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    timeSpan.textContent = getCurrentTime();
    
    contentDiv.appendChild(timeSpan);
    messageDiv.appendChild(contentDiv);
    
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Format message text with HTML (bullets, bold, line breaks)
 */
function formatMessageText(text) {
    // Escape basic HTML but keep our formatting
    let formatted = text;
    
    // Convert **bold** to <strong>
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // Convert bullet points: "• Text" or "- Text" to <li>
    const lines = formatted.split('\n');
    let inList = false;
    let result = [];
    
    for (let line of lines) {
        const trimmed = line.trim();
        
        // Check if line starts with bullet (• or -)
        if (trimmed.startsWith('•') || trimmed.match(/^-\s/)) {
            if (!inList) {
                result.push('<ul>');
                inList = true;
            }
            // Remove bullet and create list item
            const content = trimmed.replace(/^[•\-]\s*/, '');
            result.push(`<li>${content}</li>`);
        } else {
            if (inList) {
                result.push('</ul>');
                inList = false;
            }
            if (trimmed) {
                result.push(`<p>${trimmed}</p>`);
            } else {
                result.push('<br>');
            }
        }
    }
    
    if (inList) {
        result.push('</ul>');
    }
    
    return result.join('');
}

/**
 * Show typing indicator
 */
function showTypingIndicator() {
    typingIndicator.style.display = 'flex';
    scrollToBottom();
}

/**
 * Hide typing indicator
 */
function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
}

/**
 * Scroll chat to bottom
 */
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/**
 * Get current time string
 */
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('de-DE', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

/**
 * Handle input changes
 */
function handleInput() {
    sendBtn.disabled = userInput.value.trim() === '';
}

/**
 * Toggle debug panel
 */
function toggleDebug() {
    debugContent.classList.toggle('show');
}

/**
 * Update debug panel with response data
 */
function updateDebugPanel(debug) {
    if (!debug) return;
    
    // System Prompt
    if (debug.system_prompt) {
        document.getElementById('debug-system-prompt').textContent = debug.system_prompt;
    }
    
    // User Message
    if (debug.user_message) {
        document.getElementById('debug-user-message').textContent = debug.user_message;
    }
    
    // LLM Response
    if (debug.llm_response) {
        document.getElementById('debug-llm-response').textContent = 
            JSON.stringify(debug.llm_response, null, 2);
    }
    
    // Tokens
    if (debug.tokens_used) {
        document.getElementById('debug-tokens').textContent = 
            `${debug.tokens_used} tokens`;
    }
}

// Initial setup
sendBtn.disabled = true;
