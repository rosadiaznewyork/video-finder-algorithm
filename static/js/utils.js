/**
 * Utility Functions
 * Common helper functions used across the application
 */

class Utils {
    /**
     * Format view count for display
     * @param {number} count - View count
     * @returns {string} Formatted view count
     */
    static formatViewCount(count) {
        if (count >= 1000000) {
            return `${(count / 1000000).toFixed(1)}M views`;
        } else if (count >= 1000) {
            return `${(count / 1000).toFixed(1)}K views`;
        } else {
            return `${count} views`;
        }
    }

    /**
     * Format time ago from ISO string
     * @param {string} isoString - ISO date string
     * @returns {string} Formatted time ago
     */
    static getTimeAgo(isoString) {
        const date = new Date(isoString);
        const now = new Date();
        const diff = now - date;
        
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 0) {
            return `${days} day${days !== 1 ? 's' : ''} ago`;
        } else if (hours > 0) {
            return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
        } else if (minutes > 0) {
            return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
        } else {
            return "Just now";
        }
    }

    /**
     * Validate YouTube URL or video ID
     * @param {string} urlOrId - YouTube URL or video ID
     * @returns {boolean} True if valid
     */
    static isValidYouTubeUrl(urlOrId) {
        const patterns = [
            /^[a-zA-Z0-9_-]{11}$/,  // Video ID
            /youtube\.com\/watch\?v=/,  // Regular YouTube URL
            /youtu\.be\//,  // Short YouTube URL
            /youtube\.com\/embed\//,  // Embed URL
        ];
        
        return patterns.some(pattern => pattern.test(urlOrId));
    }

    /**
     * Extract video ID from YouTube URL
     * @param {string} urlOrId - YouTube URL or video ID
     * @returns {string|null} Video ID or null if invalid
     */
    static extractVideoId(urlOrId) {
        // If it's already just a video ID (11 characters)
        if (/^[a-zA-Z0-9_-]{11}$/.test(urlOrId)) {
            return urlOrId;
        }
        
        // Try different URL patterns
        const patterns = [
            /(?:youtube\.com\/watch\?v=|youtube\.com\/watch\?.*&v=)([a-zA-Z0-9_-]{11})/,
            /youtu\.be\/([a-zA-Z0-9_-]{11})/,
            /youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/,
            /youtube\.com\/v\/([a-zA-Z0-9_-]{11})/
        ];
        
        for (const pattern of patterns) {
            const match = urlOrId.match(pattern);
            if (match) {
                return match[1];
            }
        }
        
        return null;
    }

    /**
     * Debounce function to limit execution rate
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {Function} Debounced function
     */
    static debounce(func, wait) {
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

    /**
     * Store data in localStorage with expiry
     * @param {string} key - Storage key
     * @param {*} value - Value to store
     * @param {number} ttl - Time to live in milliseconds
     */
    static setWithExpiry(key, value, ttl) {
        const now = new Date();
        const item = {
            value: value,
            expiry: now.getTime() + ttl
        };
        localStorage.setItem(key, JSON.stringify(item));
    }

    /**
     * Get data from localStorage with expiry check
     * @param {string} key - Storage key
     * @returns {*} Stored value or null if expired/not found
     */
    static getWithExpiry(key) {
        const itemStr = localStorage.getItem(key);
        
        if (!itemStr) {
            return null;
        }
        
        try {
            const item = JSON.parse(itemStr);
            const now = new Date();
            
            if (now.getTime() > item.expiry) {
                localStorage.removeItem(key);
                return null;
            }
            
            return item.value;
        } catch (e) {
            return null;
        }
    }

    /**
     * Deep clone an object
     * @param {*} obj - Object to clone
     * @returns {*} Cloned object
     */
    static deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj.getTime());
        if (obj instanceof Array) return obj.map(item => this.deepClone(item));
        if (obj instanceof Object) {
            const clonedObj = {};
            for (const key in obj) {
                if (obj.hasOwnProperty(key)) {
                    clonedObj[key] = this.deepClone(obj[key]);
                }
            }
            return clonedObj;
        }
    }

    /**
     * Generate a unique ID
     * @returns {string} Unique ID
     */
    static generateId() {
        return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Parse query parameters from URL
     * @param {string} url - URL to parse (defaults to current URL)
     * @returns {Object} Query parameters as object
     */
    static parseQueryParams(url = window.location.href) {
        const params = {};
        const queryString = url.split('?')[1];
        
        if (queryString) {
            queryString.split('&').forEach(param => {
                const [key, value] = param.split('=');
                params[decodeURIComponent(key)] = decodeURIComponent(value || '');
            });
        }
        
        return params;
    }

    /**
     * Smooth scroll to element
     * @param {string} elementId - Element ID to scroll to
     * @param {number} offset - Offset from top (default 0)
     */
    static scrollToElement(elementId, offset = 0) {
        const element = document.getElementById(elementId);
        if (element) {
            const top = element.getBoundingClientRect().top + window.pageYOffset - offset;
            window.scrollTo({ top, behavior: 'smooth' });
        }
    }

    /**
     * Check if element is in viewport
     * @param {HTMLElement} element - Element to check
     * @returns {boolean} True if in viewport
     */
    static isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
}

// Export for global use
window.Utils = Utils;