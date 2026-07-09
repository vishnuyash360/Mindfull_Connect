/**
 * Main JavaScript for the Mental Health Support Platform
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
  // Initialize tooltips
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
  
  // Initialize popovers
  const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
  const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
  
  // Add a class to the current active nav link
  const currentLocation = window.location.pathname;
  const navLinks = document.querySelectorAll('.nav-link');
  
  navLinks.forEach(link => {
    if (link.getAttribute('href') === currentLocation) {
      link.classList.add('active');
    }
  });
  
  // Flash message auto-dismissal
  const flashMessages = document.querySelectorAll('.alert-dismissible');
  
  flashMessages.forEach(message => {
    // Auto-dismiss after 5 seconds (5000ms)
    setTimeout(() => {
      const closeBtn = message.querySelector('.btn-close');
      if (closeBtn) {
        closeBtn.click();
      }
    }, 5000);
  });

  // Confirm dialog for delete actions
  const confirmButtons = document.querySelectorAll('.confirm-action');
  
  confirmButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      if (!confirm('Are you sure you want to perform this action? This cannot be undone.')) {
        e.preventDefault();
      }
    });
  });
  
  // Enable responsive tables
  const tables = document.querySelectorAll('table');
  tables.forEach(table => {
    if (!table.parentElement.classList.contains('table-responsive')) {
      const wrapper = document.createElement('div');
      wrapper.classList.add('table-responsive');
      table.parentNode.insertBefore(wrapper, table);
      wrapper.appendChild(table);
    }
  });
  
  // Initialize any date pickers
  const datePickers = document.querySelectorAll('.datepicker');
  if (datePickers.length > 0) {
    datePickers.forEach(picker => {
      picker.setAttribute('type', 'datetime-local');
    });
  }
  
  // Function to show/hide password
  const togglePasswordButtons = document.querySelectorAll('.toggle-password');
  
  togglePasswordButtons.forEach(button => {
    button.addEventListener('click', function() {
      const passwordField = document.querySelector(this.getAttribute('data-target'));
      
      if (passwordField.type === 'password') {
        passwordField.type = 'text';
        this.innerHTML = '<i class="fa fa-eye-slash"></i>';
      } else {
        passwordField.type = 'password';
        this.innerHTML = '<i class="fa fa-eye"></i>';
      }
    });
  });

  // Handle "go back" functionality
  const backButtons = document.querySelectorAll('.go-back');
  
  backButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      window.history.back();
    });
  });
  
  // Accessibility - skip to content link
  const skipLink = document.querySelector('.skip-to-content');
  
  if (skipLink) {
    skipLink.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.tabIndex = -1;
        target.focus();
      }
    });
  }
  
  // Initialize custom components
  initializeCustomComponents();
});

/**
 * Initialize custom components based on data attributes
 */
function initializeCustomComponents() {
  // Check if we need to initialize mood tracker
//  if (document.querySelector('#mood-chart')) {
//    initializeMoodTracker();
//  }
  
  // Check if we need to initialize the chatbot
  if (document.querySelector('#chatbot-container')) {
    initializeChatbot();
  }
  
  // Check if we need to initialize the meditation timer
  if (document.querySelector('#meditation-timer')) {
    initializeMeditationTimer();
  }
}

/**
 * Function to format dates in a user-friendly way
 * @param {Date} date - The date to format
 * @return {string} Formatted date string
 */
function formatDate(date) {
  const now = new Date();
  const diff = now - date;
  
  // Less than a day
  if (diff < 24 * 60 * 60 * 1000) {
    // Less than an hour
    if (diff < 60 * 60 * 1000) {
      const minutes = Math.floor(diff / (60 * 1000));
      return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
    } else {
      const hours = Math.floor(diff / (60 * 60 * 1000));
      return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
    }
  }
  
  // Less than a week
  if (diff < 7 * 24 * 60 * 60 * 1000) {
    const days = Math.floor(diff / (24 * 60 * 60 * 1000));
    return `${days} day${days !== 1 ? 's' : ''} ago`;
  }
  
  // Format as date
  const options = { year: 'numeric', month: 'short', day: 'numeric' };
  return date.toLocaleDateString(undefined, options);
}

/**
 * Show a notification to the user
 * @param {string} message - The message to display
 * @param {string} type - The type of notification (success, warning, error)
 */
function showNotification(message, type = 'info') {
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
  alertDiv.setAttribute('role', 'alert');
  
  alertDiv.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  
  const container = document.querySelector('.container');
  if (container) {
    container.insertBefore(alertDiv, container.firstChild);
  } else {
    document.body.insertBefore(alertDiv, document.body.firstChild);
  }
  
  // Auto dismiss after 5 seconds
  setTimeout(() => {
    alertDiv.classList.remove('show');
    setTimeout(() => {
      alertDiv.remove();
    }, 150);
  }, 5000);
}
