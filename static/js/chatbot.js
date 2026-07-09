/**
 * Chatbot functionality
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
  initializeChatbot();
});

let chatHistory = [];

/**
 * Initialize the chatbot UI and interactions
 */
function initializeChatbot() {
  const chatMessages = document.getElementById('chat-messages');
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  
  if (!chatMessages || !chatForm || !chatInput) return;
  
  // Add welcome message
  addBotMessage("Hi there! I'm your mental health support assistant. How can I help you today?");
  
  // Handle form submission
  chatForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const message = chatInput.value.trim();
    if (message === '') return;
    
    // Add user message to chat
    addUserMessage(message);
    
    // Clear input
    chatInput.value = '';
    
    // Store in chat history
    chatHistory.push({ role: 'user', content: message });
    
    // Get bot response
    getBotResponse(message);
    
    // Scroll to bottom
    scrollToBottom();
  });
  
  // Add suggestion buttons
  const suggestionsContainer = document.getElementById('chat-suggestions');
  if (suggestionsContainer) {
    const suggestions = [
      "I'm feeling anxious",
      "What are coping strategies for stress?",
      "How can I improve my sleep?",
      "Tell me about meditation",
      "I need resources for depression"
    ];
    
    suggestions.forEach(suggestion => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'btn btn-sm btn-outline-primary me-2 mb-2';
      button.textContent = suggestion;
      
      button.addEventListener('click', function() {
        // Add user message to chat
        addUserMessage(suggestion);
        
        // Store in chat history
        chatHistory.push({ role: 'user', content: suggestion });
        
        // Get bot response
        getBotResponse(suggestion);
        
        // Scroll to bottom
        scrollToBottom();
      });
      
      suggestionsContainer.appendChild(button);
    });
  }
}

/**
 * Add a user message to the chat
 * @param {string} message - The message text
 */
function addUserMessage(message) {
  const chatMessages = document.getElementById('chat-messages');
  
  const messageElement = document.createElement('div');
  messageElement.className = 'chat-message chat-message-user';
  messageElement.textContent = message;
  
  chatMessages.appendChild(messageElement);
  scrollToBottom();
}

/**
 * Add a bot message to the chat
 * @param {string} message - The message text
 */
function addBotMessage(message) {
  const chatMessages = document.getElementById('chat-messages');
  
  // Show typing indicator
  const typingIndicator = document.createElement('div');
  typingIndicator.className = 'chat-message chat-message-bot typing-indicator';
  typingIndicator.innerHTML = '<span>.</span><span>.</span><span>.</span>';
  chatMessages.appendChild(typingIndicator);
  scrollToBottom();
  
  // Simulate typing delay
  setTimeout(() => {
    // Remove typing indicator
    chatMessages.removeChild(typingIndicator);
    
    // Add the actual message
    const messageElement = document.createElement('div');
    messageElement.className = 'chat-message chat-message-bot';
    
    // Parse URLs in the message
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const textWithLinks = message.replace(urlRegex, '<a href="$1" target="_blank">$1</a>');
    
    messageElement.innerHTML = textWithLinks;
    
    chatMessages.appendChild(messageElement);
    scrollToBottom();
    
    // Store in chat history
    chatHistory.push({ role: 'bot', content: message });
  }, 1000);
}

/**
 * Get a response from the chatbot API
 * @param {string} message - The user's message
 */
function getBotResponse(message) {
  // Make API call to the chatbot endpoint
  fetch('/chatbot/message', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message: message }),
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    if (data.error) {
      addBotMessage('Sorry, I encountered an error. Please try again later.');
    } else {
      addBotMessage(data.response);
    }
  })
  .catch(error => {
    console.error('Error:', error);
    addBotMessage('Sorry, I encountered an error. Please try again later.');
  });
}

/**
 * Scroll the chat container to the bottom
 */
function scrollToBottom() {
  const chatMessages = document.getElementById('chat-messages');
  chatMessages.scrollTop = chatMessages.scrollHeight;
}
