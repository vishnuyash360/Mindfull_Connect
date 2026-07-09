/**
 * Sentiment Analysis functionality
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
  initializeSentimentUI();
});

/**
 * Initialize UI elements for sentiment visualization
 */
function initializeSentimentUI() {
  // Find all sentiment score elements
  const sentimentElements = document.querySelectorAll('[data-sentiment-score]');
  
  sentimentElements.forEach(element => {
    const score = parseFloat(element.dataset.sentimentScore);
    
    // Skip if no valid score
    if (isNaN(score)) return;
    
    // Determine sentiment category and color
    let category, color, icon;
    
    if (score <= -0.6) {
      category = 'Very Negative';
      color = 'var(--warning-dark)';
      icon = 'fa-face-frown';
    } else if (score <= -0.2) {
      category = 'Negative';
      color = 'var(--warning-light)';
      icon = 'fa-face-meh';
    } else if (score <= 0.2) {
      category = 'Neutral';
      color = 'var(--text-light)';
      icon = 'fa-face-meh';
    } else if (score <= 0.6) {
      category = 'Positive';
      color = 'var(--secondary-light)';
      icon = 'fa-face-smile';
    } else {
      category = 'Very Positive';
      color = 'var(--secondary-dark)';
      icon = 'fa-face-laugh-beam';
    }
    
    // Create sentiment indicator
    const indicator = document.createElement('span');
    indicator.className = 'sentiment-indicator';
    indicator.innerHTML = `<i class="fas ${icon}" style="color: ${color};"></i>`;
    indicator.title = `${category} (${score.toFixed(2)})`;
    
    // Add tooltip if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
      new bootstrap.Tooltip(indicator);
    }
    
    // Add to element
    element.appendChild(indicator);
  });
  
  // Handle sentiment analysis for text inputs if needed
  const realTimeSentiment = document.querySelectorAll('[data-sentiment-analysis]');
  
  realTimeSentiment.forEach(element => {
    // Create sentiment feedback element
    const feedbackElement = document.createElement('div');
    feedbackElement.className = 'sentiment-feedback mt-2';
    feedbackElement.innerHTML = `
      <small class="text-muted">Content tone: <span class="sentiment-label">Neutral</span></small>
      <div class="progress" style="height: 5px;">
        <div class="progress-bar" role="progressbar" style="width: 50%; background-color: var(--text-light);" 
             aria-valuenow="50" aria-valuemin="0" aria-valuemax="100"></div>
      </div>
    `;
    
    // Insert after the element
    element.parentNode.insertBefore(feedbackElement, element.nextSibling);
    
    // Update on input
    element.addEventListener('input', debounce(function() {
      const text = this.value;
      
      // Simple client-side sentiment approximation
      // This is just an approximation - the server does the real analysis
      approximateSentiment(text, feedbackElement);
    }, 500));
  });
}

/**
 * Approximate sentiment for immediate feedback
 * Note: This is just for UI feedback, real sentiment analysis happens server-side
 * @param {string} text - The text to analyze
 * @param {HTMLElement} feedbackElement - The element to update with results
 */
function approximateSentiment(text, feedbackElement) {
  if (!text || text.length < 5) {
    updateSentimentFeedback(feedbackElement, 0, 'Neutral', 'var(--text-light)');
    return;
  }
  
  // Simple word lists for basic approximation
  const positiveWords = [
    'good', 'great', 'awesome', 'excellent', 'happy', 'joy', 'love', 'amazing',
    'wonderful', 'positive', 'hopeful', 'grateful', 'thankful', 'relaxed',
    'calm', 'peaceful', 'nice', 'beautiful', 'kind', 'success', 'better', 'improve'
  ];
  
  const negativeWords = [
    'bad', 'terrible', 'awful', 'horrible', 'sad', 'angry', 'upset', 'hate',
    'fear', 'worried', 'anxious', 'stress', 'depressed', 'lonely', 'tired',
    'painful', 'hurt', 'disappointing', 'fail', 'worse', 'problem', 'difficult'
  ];
  
  // Normalize text for comparison
  const normalizedText = text.toLowerCase();
  const words = normalizedText.split(/\W+/);
  
  // Count positive and negative words
  let positiveCount = 0;
  let negativeCount = 0;
  
  words.forEach(word => {
    if (positiveWords.includes(word)) positiveCount++;
    if (negativeWords.includes(word)) negativeCount++;
  });
  
  // Calculate simple score between -1 and 1
  const totalWords = words.length;
  const sentiment = (positiveCount - negativeCount) / Math.max(totalWords / 10, 1);
  
  // Clamp between -1 and 1
  const score = Math.max(-1, Math.min(1, sentiment));
  
  // Determine category and color
  let category, color;
  
  if (score <= -0.6) {
    category = 'Very Negative';
    color = 'var(--warning-dark)';
  } else if (score <= -0.2) {
    category = 'Negative';
    color = 'var(--warning-light)';
  } else if (score <= 0.2) {
    category = 'Neutral';
    color = 'var(--text-light)';
  } else if (score <= 0.6) {
    category = 'Positive';
    color = 'var(--secondary-light)';
  } else {
    category = 'Very Positive';
    color = 'var(--secondary-dark)';
  }
  
  // Update the feedback element
  updateSentimentFeedback(feedbackElement, score, category, color);
}

/**
 * Update the sentiment feedback UI
 * @param {HTMLElement} element - The feedback element to update
 * @param {number} score - Sentiment score between -1 and 1
 * @param {string} category - Sentiment category text
 * @param {string} color - CSS color for the indicator
 */
function updateSentimentFeedback(element, score, category, color) {
  const label = element.querySelector('.sentiment-label');
  const progressBar = element.querySelector('.progress-bar');
  
  if (label) label.textContent = category;
  
  if (progressBar) {
    // Convert score from [-1, 1] to [0, 100]
    const percentage = (score + 1) * 50;
    progressBar.style.width = `${percentage}%`;
    progressBar.style.backgroundColor = color;
    progressBar.setAttribute('aria-valuenow', percentage);
  }
}

/**
 * Debounce function to limit how often a function is called
 * @param {Function} func - The function to debounce
 * @param {number} wait - The debounce wait time in milliseconds
 * @return {Function} Debounced function
 */
function debounce(func, wait) {
  let timeout;
  return function() {
    const context = this;
    const args = arguments;
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      func.apply(context, args);
    }, wait);
  };
}
