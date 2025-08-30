/**
 * Main Application Controller
 * Manages application state and coordinates between views
 */

class App {
    constructor() {
        this.api = new ApiService();
        this.currentView = 'rating';
        this.views = {};
        this.initializeViews();
        this.setupEventListeners();
    }

    initializeViews() {
        this.views.recommendations = new RecommendationsView(this.api);
        this.views.liked = new LikedVideosView(this.api);
        this.views.search = new SearchView(this.api);
        this.views.history = new SearchHistoryView(this.api);
    }

    setupEventListeners() {
        // Setup search input enter key
        document.addEventListener('DOMContentLoaded', () => {
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        this.performTopicSearch();
                    }
                });
            }
            
            // Load initial view
            this.loadView('rating');
        });
    }

    /**
     * Switch between views
     */
    switchView(view) {
        this.currentView = view;
        
        // Update navigation buttons
        ['rating', 'liked', 'search', 'history'].forEach(v => {
            const btn = document.getElementById(`${v === 'rating' ? 'rating' : v}Btn`);
            const container = document.getElementById(`${v === 'rating' ? 'rating' : v}View`);
            
            if (btn) {
                btn.classList.toggle('active', v === view);
            }
            if (container) {
                container.classList.toggle('active', v === view);
            }
        });
        
        // Load appropriate data
        this.loadView(view);
    }

    loadView(view) {
        switch(view) {
            case 'rating':
                this.views.recommendations.load();
                break;
            case 'liked':
                this.views.liked.load();
                break;
            case 'search':
                // Search results are loaded by performTopicSearch
                break;
            case 'history':
                this.views.history.load();
                break;
        }
    }

    /**
     * Rate a video
     */
    async rateVideo(videoId, liked) {
        const likeBtn = document.getElementById(`like-${videoId}`);
        const dislikeBtn = document.getElementById(`dislike-${videoId}`);
        
        // Disable buttons during request
        if (likeBtn) likeBtn.disabled = true;
        if (dislikeBtn) dislikeBtn.disabled = true;
        
        try {
            const result = await this.api.rateVideo(videoId, liked);
            
            if (result.success) {
                // Update button states
                if (likeBtn) {
                    likeBtn.classList.remove('liked');
                    likeBtn.textContent = '👍 Like';
                }
                if (dislikeBtn) {
                    dislikeBtn.classList.remove('disliked');
                    dislikeBtn.textContent = '👎 Dislike';
                }
                
                if (liked && likeBtn) {
                    likeBtn.classList.add('liked');
                    likeBtn.textContent = '👍 Liked';
                } else if (!liked && dislikeBtn) {
                    dislikeBtn.classList.add('disliked');
                    dislikeBtn.textContent = '👎 Disliked';
                }
                
                NotificationManager.show(liked ? 'Video liked! 👍' : 'Video disliked! 👎');
                
                // Refresh recommendations if model was retrained
                if (result.model_retrained) {
                    setTimeout(() => {
                        NotificationManager.show('🤖 AI model updated with your feedback!');
                        if (this.currentView === 'rating') {
                            this.views.recommendations.load();
                        }
                    }, 1500);
                }
            } else {
                throw new Error(result.error || 'Failed to rate video');
            }
        } catch (error) {
            console.error('Error rating video:', error);
            NotificationManager.show('Failed to rate video: ' + error.message);
        }
        
        // Re-enable buttons
        if (likeBtn) likeBtn.disabled = false;
        if (dislikeBtn) dislikeBtn.disabled = false;
    }

    /**
     * Remove a liked video
     */
    async removeLikedVideo(videoId) {
        const removeBtn = document.getElementById(`remove-${videoId}`);
        const videoCard = document.getElementById(`liked-card-${videoId}`);
        
        if (removeBtn) {
            removeBtn.disabled = true;
            removeBtn.textContent = '🗑️ Removing...';
        }
        
        try {
            const result = await this.api.removeLikedVideo(videoId);
            
            if (result.success) {
                // Remove video card with animation
                if (videoCard) {
                    videoCard.style.transition = 'all 0.3s ease';
                    videoCard.style.transform = 'scale(0.8)';
                    videoCard.style.opacity = '0';
                    
                    setTimeout(() => {
                        videoCard.remove();
                        
                        // Check if there are any videos left
                        const remainingCards = document.querySelectorAll('#likedVideoGrid .video-card');
                        if (remainingCards.length === 0) {
                            this.views.liked.displayVideos([]);
                        } else {
                            this.views.liked.updateStatusBar(remainingCards.length);
                        }
                    }, 300);
                }
                
                NotificationManager.show('Video removed from MyTube 🗑️');
                
                if (result.model_retrained) {
                    setTimeout(() => {
                        NotificationManager.show('🤖 AI model updated with your changes!');
                    }, 1500);
                }
            } else {
                throw new Error(result.error || 'Failed to remove video');
            }
        } catch (error) {
            console.error('Error removing video:', error);
            NotificationManager.show('Failed to remove video: ' + error.message);
            
            if (removeBtn) {
                removeBtn.disabled = false;
                removeBtn.textContent = '🗑️ Remove';
            }
        }
    }

    /**
     * Perform topic search
     */
    async performTopicSearch() {
        const searchInput = document.getElementById('searchInput');
        const searchButton = document.getElementById('searchButton');
        const topic = searchInput ? searchInput.value.trim() : '';
        
        if (!topic) {
            NotificationManager.show('Please enter a search topic');
            if (searchInput) searchInput.focus();
            return;
        }
        
        if (topic.length < 3) {
            NotificationManager.show('Search topic must be at least 3 characters');
            if (searchInput) searchInput.focus();
            return;
        }
        
        // Show loading state
        if (searchButton) {
            searchButton.disabled = true;
            searchButton.textContent = '🔍 Searching...';
        }
        
        // Switch to search results view
        this.switchView('search');
        const searchBtn = document.getElementById('searchBtn');
        if (searchBtn) {
            searchBtn.style.display = 'inline-block';
        }
        
        this.views.search.showLoading(topic);
        
        try {
            const result = await this.api.searchByTopic(topic);
            
            if (result.success) {
                this.views.search.displayResults(result);
                NotificationManager.show(`Found ${result.total_videos} videos for "${topic}" 🎯`);
            } else {
                throw new Error(result.error || 'Search failed');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.views.search.displayError(error.message, topic);
            NotificationManager.show('Search failed: ' + error.message);
        } finally {
            if (searchButton) {
                searchButton.disabled = false;
                searchButton.textContent = '🔍';
            }
        }
    }

    /**
     * Clear search results
     */
    clearSearchResults() {
        const searchBtn = document.getElementById('searchBtn');
        if (searchBtn) {
            searchBtn.style.display = 'none';
        }
        
        this.views.search.clear();
        
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.value = '';
        }
        
        this.switchView('rating');
    }

    /**
     * Add video by URL
     */
    async addVideoByUrl() {
        const input = document.getElementById('addVideoInput');
        const button = document.getElementById('addVideoButton');
        const url = input ? input.value.trim() : '';
        
        if (!url) {
            NotificationManager.show('Please enter a YouTube URL or video ID');
            if (input) input.focus();
            return;
        }
        
        if (!Utils.isValidYouTubeUrl(url)) {
            NotificationManager.show('Invalid YouTube URL format. Please check and try again.');
            if (input) input.focus();
            return;
        }
        
        if (button) {
            button.disabled = true;
            button.textContent = 'Adding...';
        }
        if (input) {
            input.disabled = true;
        }
        
        try {
            const result = await this.api.addVideoByUrl(url);
            
            if (result.success) {
                if (input) input.value = '';
                
                NotificationManager.show(`✅ Added "${result.video.title}" to MyTube!`);
                
                // Reload liked videos
                this.views.liked.load();
                
                if (result.model_retrained) {
                    setTimeout(() => {
                        NotificationManager.show('🤖 AI model updated with your new preference!');
                    }, 1500);
                }
            } else {
                NotificationManager.show('❌ ' + (result.error || 'Failed to add video'));
            }
        } catch (error) {
            console.error('Error adding video:', error);
            if (error.status === 409) {
                NotificationManager.show('⚠️ Video already in your liked videos');
            } else if (error.status === 404) {
                NotificationManager.show('❌ Video not found. Check if it exists and is public.');
            } else {
                NotificationManager.show('❌ Failed to add video: ' + error.message);
            }
        } finally {
            if (button) {
                button.disabled = false;
                button.textContent = 'Add Video';
            }
            if (input) {
                input.disabled = false;
                input.focus();
            }
        }
    }

    /**
     * View session videos
     */
    async viewSessionVideos(sessionId, topic) {
        try {
            const data = await this.api.getSearchSessionVideos(sessionId);
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to load session videos');
            }
            
            this.views.history.displaySessionVideos(data.videos, topic);
            NotificationManager.show(`Viewing ${data.videos.length} videos from "${topic}" search`);
            
        } catch (error) {
            console.error('Error loading session videos:', error);
            NotificationManager.show('Failed to load session videos: ' + error.message);
        }
    }

    /**
     * Delete search session
     */
    async deleteSearchSession(sessionId) {
        if (!confirm('Are you sure you want to delete this search session? This cannot be undone.')) {
            return;
        }
        
        try {
            const result = await this.api.deleteSearchSession(sessionId, false);
            
            if (result.success) {
                const sessionCard = document.getElementById(`session-${sessionId}`);
                if (sessionCard) {
                    sessionCard.style.transition = 'all 0.3s ease';
                    sessionCard.style.transform = 'scale(0.8)';
                    sessionCard.style.opacity = '0';
                    
                    setTimeout(() => {
                        sessionCard.remove();
                    }, 300);
                }
                
                NotificationManager.show('Search session deleted 🗑️');
                
                setTimeout(() => {
                    this.loadSearchHistory();
                }, 1000);
            } else {
                throw new Error(result.error || 'Failed to delete search session');
            }
        } catch (error) {
            console.error('Error deleting search session:', error);
            NotificationManager.show('Failed to delete session: ' + error.message);
        }
    }

    /**
     * Load search history
     */
    loadSearchHistory() {
        this.views.history.load();
    }

    /**
     * Clean up old searches
     */
    async cleanupSearches() {
        const cleanupBtn = document.getElementById('cleanupBtn');
        const daysInput = document.getElementById('cleanupDays');
        const daysOld = daysInput ? parseInt(daysInput.value) || 7 : 7;
        
        if (daysOld < 1) {
            NotificationManager.show('Days must be at least 1');
            return;
        }
        
        if (!confirm(`Are you sure you want to archive search sessions older than ${daysOld} days?`)) {
            return;
        }
        
        if (cleanupBtn) {
            cleanupBtn.disabled = true;
            cleanupBtn.textContent = 'Cleaning Up...';
        }
        
        try {
            const result = await this.api.cleanupSearches(daysOld);
            
            if (result.success) {
                NotificationManager.show(result.message + ' 🧹');
                
                setTimeout(() => {
                    this.loadSearchHistory();
                }, 1500);
            } else {
                throw new Error(result.error || 'Failed to cleanup searches');
            }
        } catch (error) {
            console.error('Error cleaning up searches:', error);
            NotificationManager.show('Failed to cleanup searches: ' + error.message);
        } finally {
            if (cleanupBtn) {
                cleanupBtn.disabled = false;
                cleanupBtn.textContent = 'Clean Up';
            }
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});

// Export static methods for onclick handlers
window.App = {
    rateVideo: (videoId, liked) => window.app.rateVideo(videoId, liked),
    removeLikedVideo: (videoId) => window.app.removeLikedVideo(videoId),
    performTopicSearch: () => window.app.performTopicSearch(),
    clearSearchResults: () => window.app.clearSearchResults(),
    addVideoByUrl: () => window.app.addVideoByUrl(),
    viewSessionVideos: (sessionId, topic) => window.app.viewSessionVideos(sessionId, topic),
    deleteSearchSession: (sessionId) => window.app.deleteSearchSession(sessionId),
    loadSearchHistory: () => window.app.loadSearchHistory(),
    cleanupSearches: () => window.app.cleanupSearches(),
    switchView: (view) => window.app.switchView(view)
};