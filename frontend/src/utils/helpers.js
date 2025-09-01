/**
 * Helper utility functions
 */

/**
 * Open a video URL in a new tab
 * @param {string} url - The video URL to open
 */
export function openVideo(url) {
  window.open(url, '_blank');
}

/**
 * Get CSS class for confidence level
 * @param {number} confidence - Confidence percentage (0-100)
 * @returns {string} CSS class name
 */
export function getConfidenceClass(confidence) {
  if (confidence >= 70) return 'confidence-high';
  if (confidence >= 40) return 'confidence-medium';
  return 'confidence-low';
}

/**
 * Parse error message to determine error type
 * @param {string} errorMessage - The error message to parse
 * @returns {string} Error type identifier
 */
export function parseErrorType(errorMessage) {
  const message = errorMessage.toLowerCase();
  
  if (message.includes('quota')) {
    return 'quota_exceeded';
  } else if (message.includes('api') && message.includes('key')) {
    return 'invalid_api_key';
  } else if (message.includes('network') || message.includes('fetch')) {
    return 'network_error';
  }
  
  return 'unknown';
}

/**
 * Debounce function to limit how often a function can be called
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
export function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}
