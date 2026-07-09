/**
 * Meditation Timer functionality
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
  initializeMeditationTimer();
});

let timerInterval;
let timerStartTime;
let timerDuration;
let timerPaused = false;
let timerPausedTime = 0;
let chimeAudio;

/**
 * Initialize the meditation timer
 */
function initializeMeditationTimer() {
  const timerContainer = document.getElementById('meditation-timer');
  
  if (!timerContainer) return;
  
  // Get timer elements
  const timerDisplay = document.getElementById('timer-display');
  const startButton = document.getElementById('timer-start');
  const pauseButton = document.getElementById('timer-pause');
  const resetButton = document.getElementById('timer-reset');
  const presetButtons = document.querySelectorAll('.timer-preset');
  
  // Initialize chime sound
  chimeAudio = new Audio('https://soundbible.com/grab.php?id=1815&type=mp3');  // Meditation bell sound
  
  // Set up event listeners for preset buttons
  presetButtons.forEach(button => {
    button.addEventListener('click', function() {
      const minutes = parseInt(this.dataset.minutes, 10);
      setTimerDuration(minutes * 60);
      
      // Update active state
      presetButtons.forEach(btn => btn.classList.remove('active'));
      this.classList.add('active');
    });
  });
  
  // Set up start button
  startButton.addEventListener('click', function() {
    if (!timerDuration) {
      // Default to 5 minutes if no duration is set
      setTimerDuration(5 * 60);
    }
    
    if (timerPaused) {
      // Resume timer
      timerPaused = false;
      timerStartTime = Date.now() - timerPausedTime;
      this.textContent = 'Start';
      pauseButton.textContent = 'Pause';
      pauseButton.disabled = false;
    } else {
      // Start timer
      timerStartTime = Date.now();
      this.disabled = true;
      pauseButton.disabled = false;
    }
    
    // Clear any existing interval
    clearInterval(timerInterval);
    
    // Start the interval
    timerInterval = setInterval(updateTimer, 1000);
    
    // Show notification
    showNotification('Meditation timer started', 'info');
  });
  
  // Set up pause button
  pauseButton.addEventListener('click', function() {
    if (timerPaused) {
      // Resume timer
      timerPaused = false;
      timerStartTime = Date.now() - timerPausedTime;
      this.textContent = 'Pause';
      startButton.textContent = 'Start';
      
      // Restart the interval
      clearInterval(timerInterval);
      timerInterval = setInterval(updateTimer, 1000);
    } else {
      // Pause timer
      timerPaused = true;
      timerPausedTime = Date.now() - timerStartTime;
      this.textContent = 'Resume';
      startButton.textContent = 'Restart';
      startButton.disabled = false;
      
      // Clear the interval
      clearInterval(timerInterval);
    }
  });
  
  // Set up reset button
  resetButton.addEventListener('click', function() {
    // Reset timer
    clearInterval(timerInterval);
    timerPaused = false;
    timerPausedTime = 0;
    
    // Reset display
    timerDisplay.textContent = formatTime(timerDuration || 0);
    
    // Reset buttons
    startButton.disabled = false;
    startButton.textContent = 'Start';
    pauseButton.disabled = true;
    pauseButton.textContent = 'Pause';
  });
  
  // Initialize with 5 minute preset
  setTimerDuration(5 * 60);
  document.querySelector('[data-minutes="5"]').classList.add('active');
}

/**
 * Set the timer duration
 * @param {number} seconds - The duration in seconds
 */
function setTimerDuration(seconds) {
  timerDuration = seconds;
  
  const timerDisplay = document.getElementById('timer-display');
  timerDisplay.textContent = formatTime(seconds);
  
  // Reset timer state
  clearInterval(timerInterval);
  timerPaused = false;
  timerPausedTime = 0;
  
  // Reset buttons
  const startButton = document.getElementById('timer-start');
  const pauseButton = document.getElementById('timer-pause');
  
  startButton.disabled = false;
  startButton.textContent = 'Start';
  pauseButton.disabled = true;
  pauseButton.textContent = 'Pause';
}

/**
 * Update the timer display
 */
function updateTimer() {
  const timerDisplay = document.getElementById('timer-display');
  const elapsedTime = Math.floor((Date.now() - timerStartTime) / 1000);
  const remainingTime = timerDuration - elapsedTime;
  
  if (remainingTime <= 0) {
    // Timer finished
    clearInterval(timerInterval);
    timerDisplay.textContent = '00:00';
    
    // Play chime sound
    playChime();
    
    // Reset buttons
    const startButton = document.getElementById('timer-start');
    const pauseButton = document.getElementById('timer-pause');
    
    startButton.disabled = false;
    pauseButton.disabled = true;
    
    // Show completion message
    showCompletionMessage();
  } else {
    // Update display
    timerDisplay.textContent = formatTime(remainingTime);
  }
}

/**
 * Format time in seconds to MM:SS
 * @param {number} seconds - Time in seconds
 * @return {string} Formatted time string
 */
function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Play the chime sound
 */
function playChime() {
  if (chimeAudio) {
    chimeAudio.currentTime = 0;
    chimeAudio.play().catch(error => {
      console.warn('Could not play audio:', error);
    });
  }
}

/**
 * Show the meditation completion message
 */
function showCompletionMessage() {
  const completionMessage = document.getElementById('completion-message');
  
  if (completionMessage) {
    completionMessage.classList.remove('d-none');
    
    // Add completion content
    completionMessage.innerHTML = `
      <div class="alert alert-success">
        <h4>Meditation Complete</h4>
        <p>Well done! You've completed your meditation session.</p>
        <p>Take a moment to notice how you feel right now. Is there a difference from when you started?</p>
        <div class="mt-3">
          <button class="btn btn-primary" onclick="document.getElementById('completion-message').classList.add('d-none')">
            Close
          </button>
          <a href="/profile/mood-tracker" class="btn btn-outline-primary ms-2">
            Record Your Mood
          </a>
        </div>
      </div>
    `;
  } else {
    // If the element doesn't exist, use a notification
    showNotification('Meditation complete! Well done.', 'success');
  }
}
