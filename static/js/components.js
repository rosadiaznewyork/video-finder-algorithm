/**
 * Reusable UI Components
 * Centralized component creation and management
 */

class VideoCard {
    /**
     * Create a video card component
     * @param {Object} video - Video data object
     * @param {Object} options - Rendering options
     * @returns {string} HTML string for video card
     */
    static create(video, options = {}) {
        const defaultOptions = {
            showRating: true,
            showRemove: false,
            showConfidence: false,
            confidenceLabel: 'match',
            cardIdPrefix: '',
            badges: []
        };
        
        const opts = { ...defaultOptions, ...options };
        
        return `
            <div class="video-card" ${opts.cardIdPrefix ? `id="${opts.cardIdPrefix}${video.id}"` : ''}>
                ${this.renderThumbnail(video, opts)}
                ${this.renderInfo(video, opts)}
            </div>
        `;
    }

    static renderThumbnail(video, options) {
        const thumbnail = video.thumbnail || `https://img.youtube.com/vi/${video.id}/hqdefault.jpg`;
        const badges = [];
        
        if (options.showConfidence && video.confidence !== undefined) {
            const confidenceClass = this.getConfidenceClass(video.confidence);
            badges.push(`
                <div class="confidence-badge ${confidenceClass}">
                    ${video.confidence}% ${options.confidenceLabel}
                </div>
            `);
        }
        
        options.badges.forEach(badge => {
            badges.push(`
                <div class="confidence-badge" style="${badge.style || ''}">
                    ${badge.text}
                </div>
            `);
        });
        
        return `
            <div class="video-thumbnail" onclick="VideoCard.openVideo('${video.url}')">
                <img src="${thumbnail}" 
                     alt="${this.escapeHtml(video.title)}" 
                     onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22320%22 height=%22180%22><rect width=%22100%%22 height=%22100%%22 fill=%22%23333%22/><text x=%2250%%22 y=%2250%%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22>No Image</text></svg>'">
                ${badges.join('')}
            </div>
        `;
    }

    static renderInfo(video, options) {
        return `
            <div class="video-info">
                <div class="video-title" onclick="VideoCard.openVideo('${video.url}')" style="cursor: pointer;">
                    ${this.escapeHtml(video.title)}
                </div>
                <div class="video-meta">
                    <span>${this.escapeHtml(video.channel_name)}</span>
                    <span>•</span>
                    <span>${video.views_formatted || Utils.formatViewCount(video.view_count)}</span>
                </div>
                ${options.showRating ? this.renderRatingButtons(video) : ''}
                ${options.showRemove ? this.renderRemoveButton(video) : ''}
            </div>
        `;
    }

    static renderRatingButtons(video) {
        return `
            <div class="rating-buttons">
                <button class="rating-btn like-btn" 
                        onclick="App.rateVideo('${video.id}', true)" 
                        id="like-${video.id}">
                    👍 Like
                </button>
                <button class="rating-btn dislike-btn" 
                        onclick="App.rateVideo('${video.id}', false)" 
                        id="dislike-${video.id}">
                    👎 Dislike
                </button>
            </div>
        `;
    }

    static renderRemoveButton(video) {
        return `
            <button class="remove-btn" 
                    onclick="App.removeLikedVideo('${video.id}')" 
                    id="remove-${video.id}">
                🗑️ Remove
            </button>
        `;
    }

    static getConfidenceClass(confidence) {
        if (confidence >= 70) return 'confidence-high';
        if (confidence >= 50) return 'confidence-medium';
        return 'confidence-low';
    }

    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    static openVideo(url) {
        window.open(url, '_blank');
    }
}

class NotificationManager {
    static notifications = [];
    
    /**
     * Show a notification message
     * @param {string} message - Notification message
     * @param {number} duration - Duration in milliseconds (default 3000)
     */
    static show(message, duration = 3000) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #333;
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            z-index: 1000;
            transition: all 0.3s ease;
            transform: translateX(100%);
            max-width: 400px;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        this.notifications.push(notification);
        
        // Position multiple notifications
        const offset = (this.notifications.length - 1) * 60;
        notification.style.top = `${20 + offset}px`;
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after duration
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(notification);
                const index = this.notifications.indexOf(notification);
                if (index > -1) {
                    this.notifications.splice(index, 1);
                }
                // Reposition remaining notifications
                this.repositionNotifications();
            }, 300);
        }, duration);
    }
    
    static repositionNotifications() {
        this.notifications.forEach((notification, index) => {
            notification.style.top = `${20 + index * 60}px`;
        });
    }
}

class LoadingState {
    /**
     * Create a loading state component
     * @param {string} message - Loading message
     * @param {boolean} showSpinner - Whether to show spinner
     * @returns {string} HTML string for loading state
     */
    static create(message, showSpinner = true) {
        return `
            <div class="loading" style="grid-column: 1 / -1;">
                ${showSpinner ? '<div class="loading-spinner"></div>' : ''}
                <div>${message}</div>
            </div>
        `;
    }
}

class StatusBar {
    /**
     * Update the status bar content
     * @param {string} content - HTML content for status bar
     * @param {string} type - Status type (trained, learning, etc.)
     */
    static update(content, type = 'trained') {
        const statusBar = document.getElementById('statusBar');
        if (statusBar) {
            statusBar.innerHTML = `
                <div class="status-${type}">
                    ${content}
                </div>
            `;
        }
    }
    
    static updateForModel(modelTrained, totalRatings) {
        if (modelTrained) {
            this.update(
                `🤖 AI Model Active • Trained on ${totalRatings} video ratings • Showing personalized recommendations`,
                'trained'
            );
        } else {
            const needed = 10 - totalRatings;
            this.update(
                `📚 Learning Mode • Need ${needed} more ratings to activate AI recommendations`,
                'learning'
            );
        }
    }
}

class SearchSessionCard {
    /**
     * Create a search session card
     * @param {Object} session - Session data
     * @returns {string} HTML string for session card
     */
    static create(session) {
        return `
            <div class="search-session-card" id="session-${session.id}">
                <div class="search-session-header">
                    <div>
                        <div class="search-session-topic">${session.topic}</div>
                        <div class="search-session-meta">
                            <span>${session.video_count} videos</span>
                            <span>•</span>
                            <span>${session.time_ago}</span>
                            <span>•</span>
                            <span class="status-${session.status}">${session.status}</span>
                        </div>
                    </div>
                    <div class="search-session-actions">
                        <button class="session-action-btn" 
                                onclick="App.viewSessionVideos('${session.id}', '${session.topic}')">
                            👀 View Videos
                        </button>
                        <button class="session-action-btn delete-btn" 
                                onclick="App.deleteSearchSession('${session.id}')">
                            🗑️ Delete
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
}

// Export components for global use
window.VideoCard = VideoCard;
window.NotificationManager = NotificationManager;
window.LoadingState = LoadingState;
window.StatusBar = StatusBar;
window.SearchSessionCard = SearchSessionCard;