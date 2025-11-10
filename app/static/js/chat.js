/**
 * Chat Interface JavaScript
 * Handles message sending, UI updates, and debug panel
 */

// Global state
let conversationHistory = [];
let currentSessionId = null;
let currentWorkflowMode = 'info';  // info, contract, comparison
let contractData = {};

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
        
        // Handle LLM actions (tariffs, forms, workflow switches)
        handleLLMActions(response);
        
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
            conversation_history: conversationHistory,
            session_id: currentSessionId
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
 * Add message to chat UI with HTML formatting support and optional tariff buttons
 */
function addMessageToChat(role, text, tariffs = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Convert markdown-like formatting to HTML
    const formattedText = formatMessageText(text);
    contentDiv.innerHTML = formattedText;
    
    // Add tariff buttons if this is a bot message with tariffs
    if (role === 'bot' && tariffs && tariffs.length > 0) {
        const buttonsContainer = document.createElement('div');
        buttonsContainer.className = 'tariff-buttons-container';
        
        tariffs.forEach(tariff => {
            const button = document.createElement('button');
            button.className = 'tariff-select-btn';
            button.textContent = `${tariff.name} abschließen`;
            button.onclick = () => handleTariffSelection(tariff);
            buttonsContainer.appendChild(button);
        });
        
        contentDiv.appendChild(buttonsContainer);
    }
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    timeSpan.textContent = getCurrentTime();
    
    contentDiv.appendChild(timeSpan);
    messageDiv.appendChild(contentDiv);
    
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
    
    return messageDiv;  // Return for progress indicator
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

/**
 * Handle tariff selection and start contract workflow
 */
async function handleTariffSelection(tariffData) {
    // Add user selection message
    addMessageToChat('user', `Ich möchte den Tarif "${tariffData.name}" abschließen`);
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Extract birthdate from conversation history (DD.MM.YYYY format)
        let birthdate = null;
        const birthdatePattern = /\b(\d{2})\.(\d{2})\.(\d{4})\b/;
        for (let i = conversationHistory.length - 1; i >= 0; i--) {
            const msg = conversationHistory[i];
            if (msg.role === 'user') {
                const match = msg.content.match(birthdatePattern);
                if (match) {
                    birthdate = match[0];
                    break;
                }
            }
        }
        
        console.log('Extracted birthdate for contract:', birthdate);
        
        // Initialize contract
        const initResponse = await fetch('/api/contract/init', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tariff: tariffData,
                session_id: currentSessionId,
                birthdate: birthdate
            })
        });
        
        if (!initResponse.ok) {
            throw new Error(`HTTP error! status: ${initResponse.status}`);
        }
        
        const initData = await initResponse.json();
        currentSessionId = initData.session_id;
        currentWorkflowMode = 'contract';
        
        // Send initial message to LLM to start contract process
        const message = `Ich möchte den Tarif "${tariffData.name}" abschließen. Bitte führe mich durch den Prozess.`;
        const response = await sendMessage(message);
        
        hideTypingIndicator();
        
        // Handle LLM response (might contain show_form action)
        handleLLMActions(response);
        
    } catch (error) {
        hideTypingIndicator();
        console.error('Contract start error:', error);
        addMessageToChat('bot', 'Entschuldigung, es gab einen Fehler beim Starten des Abschlusses.');
    }
}

/**
 * Add progress indicator to bot message if contract workflow active
 */
function addProgressIndicator(messageDiv, progressInfo) {
    if (!progressInfo) return;
    
    const { current_step, total_steps, step_name } = progressInfo;
    
    // Create progress indicator
    const progressDiv = document.createElement('div');
    progressDiv.className = 'contract-progress-indicator';
    progressDiv.innerHTML = `
        <div class="progress-text">
            <span class="step-label">Schritt ${current_step} von ${total_steps}</span>
            <span class="step-name">${step_name}</span>
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: ${(current_step / total_steps) * 100}%"></div>
        </div>
    `;
    
    // Insert at the top of bot message content
    const messageContent = messageDiv.querySelector('.message-content');
    if (messageContent) {
        messageContent.insertBefore(progressDiv, messageContent.firstChild);
    }
}

/**
 * Handle LLM actions (show_form, switch_workflow, tariffs, etc.)
 */
function handleLLMActions(response) {
    // Always show bot reply first (if exists)
    // Include tariffs for buttons if present
    if (response.reply) {
        const botMessage = addMessageToChat('bot', response.reply, response.tariffs);
        
        // Add progress indicator if contract workflow active
        if (response.contract_progress) {
            addProgressIndicator(botMessage, response.contract_progress);
        }
    }
    
    // Check for function result actions
    const debug = response.debug || {};
    const functionResult = debug.function_result;
    
    if (functionResult && functionResult.action) {
        switch(functionResult.action) {
            case 'show_form':
                showFormInChat(functionResult.form_type, functionResult.context_message, functionResult.prefill_data);
                break;
                
            case 'switch_workflow':
                currentWorkflowMode = functionResult.target_workflow;
                console.log(`Switched to ${functionResult.target_workflow} workflow. State preserved: ${functionResult.state_preserved}`);
                break;
                
            case 'save_form_data':
                console.log(`Form data saved: ${functionResult.form_type}. Progress: ${functionResult.progress}%`);
                // If there's a next form, LLM will call show_form in follow-up
                break;
        }
    }
}

/**
 * Show form in chat (inline) - REAL IMPLEMENTATION
 */
function showFormInChat(formType, contextMessage, prefillData = {}) {
    console.log(`Showing form: ${formType}`, prefillData);
    
    // Render actual form using contract_forms.js
    const formHtml = renderForm(formType, prefillData, contextMessage);
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-bot';
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = formHtml;
    
    // Add form submit handler
    const form = contentDiv.querySelector('form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleFormSubmit(form);
        });
    }
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Handle form submission - REAL IMPLEMENTATION
 */
async function handleFormSubmit(form) {
    const formType = form.dataset.formType;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    console.log(`Form submitted: ${formType}`, data);
    
    // Disable form to prevent double submission
    const formElements = form.querySelectorAll('input, select, button');
    formElements.forEach(el => el.disabled = true);
    
    showTypingIndicator();
    
    try {
        // Save form data via API
        const saveResponse = await fetch('/api/contract/form/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                form_type: formType,
                data: data
            })
        });
        
        if (!saveResponse.ok) {
            throw new Error(`HTTP error! status: ${saveResponse.status}`);
        }
        
        const saveData = await saveResponse.json();
        console.log('Form saved:', saveData);
        
        // Tell LLM that form was submitted
        const message = `Formular ${formType} wurde ausgefüllt. Was ist der nächste Schritt?`;
        const response = await sendMessage(message);
        
        hideTypingIndicator();
        
        // Handle LLM response (likely shows next form)
        handleLLMActions(response);
        
    } catch (error) {
        hideTypingIndicator();
        console.error('Form submit error:', error);
        addMessageToChat('bot', 'Es gab einen Fehler beim Speichern der Daten. Bitte versuchen Sie es erneut.');
        
        // Re-enable form on error
        formElements.forEach(el => el.disabled = false);
    }
}

// Initial setup
sendBtn.disabled = true;
