// Zby Consultant Chat Handler

if (document.getElementById('chat-form')) {
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = chatInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessage(message, 'user');
        chatInput.value = '';
        
        // Show typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message message-bot typing';
        typingDiv.innerHTML = '<div class="message-avatar">🤖</div><div class="message-content"><p>Zby is typing...</p></div>';
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        try {
            const response = await fetch('/api/consult', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            
            const result = await response.json();
            
            typingDiv.remove();
            
            if (result.success) {
                addMessage(result.response, 'bot');
            } else {
                addMessage('Sorry, I\'m having trouble responding. Please ensure Ollama is running.', 'bot');
            }
        } catch (error) {
            typingDiv.remove();
            addMessage('Network error. Please try again.', 'bot');
        }
    });
}

function addMessage(text, sender) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${sender}`;
    
    const avatar = sender === 'bot' ? '🤖' : '👤';
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <p>${text.replace(/\n/g, '<br>')}</p>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Add chat styles
const chatStyle = document.createElement('style');
chatStyle.textContent = `
.chat-container {
    max-width: 800px;
    margin: 0 auto;
    height: calc(100vh - 300px);
    display: flex;
    flex-direction: column;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    overflow: hidden;
}

.chat-messages {
    flex: 1;
    padding: 2rem;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.message {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
}

.message-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: linear-gradient(135deg, #00F0FF, #00FF88);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    flex-shrink: 0;
}

.message-user .message-avatar {
    background: linear-gradient(135deg, #E53E3E, #FF006E);
}

.message-content {
    flex: 1;
    background: rgba(255, 255, 255, 0.05);
    padding: 1rem;
    border-radius: 12px;
}

.message-content p {
    margin: 0;
    line-height: 1.6;
}

.chat-form {
    padding: 1.5rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    gap: 1rem;
}

.chat-form input {
    flex: 1;
    padding: 0.75rem 1rem;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: white;
    font-size: 1rem;
}

.chat-form input:focus {
    outline: none;
    border-color: #00F0FF;
}

.job-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.job-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.match-score {
    background: linear-gradient(135deg, #00F0FF, #00FF88);
    color: #0A0E27;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.875rem;
}

.job-company, .job-location, .job-platform {
    color: rgba(255, 255, 255, 0.7);
    font-size: 0.875rem;
    margin-bottom: 0.25rem;
}

.job-actions {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
}

.upload-area {
    border: 2px dashed rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    padding: 4rem 2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    margin-bottom: 2rem;
}

.upload-area:hover, .upload-area.dragover {
    border-color: #00F0FF;
    background: rgba(0, 240, 255, 0.05);
}

.upload-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}

.parse-result {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 2rem;
    margin-top: 2rem;
}

.cv-field {
    display: flex;
    gap: 1rem;
    padding: 1rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.cv-field label {
    font-weight: 600;
    min-width: 120px;
}
`;
document.head.appendChild(chatStyle);
