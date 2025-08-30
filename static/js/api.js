/**
 * API Service Layer
 * Centralized API communication with consistent error handling
 */

class ApiError extends Error {
    constructor(message, status) {
        super(message);
        this.status = status;
        this.name = 'ApiError';
    }
}

class ApiService {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    /**
     * Generic request method with error handling
     */
    async request(endpoint, options = {}) {
        try {
            const response = await fetch(this.baseUrl + endpoint, {
                ...options,
                headers: {
                    ...this.defaultHeaders,
                    ...options.headers,
                },
            });

            const data = await response.json();

            if (!response.ok && !data.success) {
                throw new ApiError(data.error || `HTTP ${response.status}`, response.status);
            }

            return data;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(`Network error: ${error.message}`, 0);
        }
    }

    /**
     * GET request helper
     */
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    /**
     * POST request helper
     */
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    /**
     * DELETE request helper
     */
    async delete(endpoint, data = null) {
        const options = { method: 'DELETE' };
        if (data) {
            options.body = JSON.stringify(data);
        }
        return this.request(endpoint, options);
    }

    // ============= Specific API Methods =============

    /**
     * Get video recommendations
     */
    async getRecommendations() {
        return this.get('/api/recommendations');
    }

    /**
     * Rate a video
     */
    async rateVideo(videoId, liked) {
        return this.post('/api/rate', {
            video_id: videoId,
            liked: liked
        });
    }

    /**
     * Get liked videos
     */
    async getLikedVideos() {
        return this.get('/api/liked');
    }

    /**
     * Remove a liked video
     */
    async removeLikedVideo(videoId) {
        return this.post('/api/remove-liked', {
            video_id: videoId
        });
    }

    /**
     * Search for videos by topic
     */
    async searchByTopic(topic) {
        return this.post('/api/search-topic', {
            topic: topic
        });
    }

    /**
     * Get search history
     */
    async getSearchHistory() {
        return this.get('/api/search-history');
    }

    /**
     * Get videos from a search session
     */
    async getSearchSessionVideos(sessionId) {
        return this.get(`/api/search-session/${sessionId}`);
    }

    /**
     * Delete a search session
     */
    async deleteSearchSession(sessionId, removeVideos = false) {
        return this.delete(`/api/delete-search-session/${sessionId}`, {
            remove_videos: removeVideos
        });
    }

    /**
     * Clean up old search sessions
     */
    async cleanupSearches(daysOld) {
        return this.post('/api/cleanup-searches', {
            days_old: daysOld
        });
    }

    /**
     * Add a video by URL
     */
    async addVideoByUrl(url) {
        return this.post('/api/add-video-by-url', {
            url: url
        });
    }
}

// Export for use in other modules
window.ApiService = ApiService;
window.ApiError = ApiError;