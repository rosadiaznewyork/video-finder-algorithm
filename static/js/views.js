/**
 * View-specific Logic
 * Manages different views and their interactions
 */

class RecommendationsView {
    constructor(apiService) {
        this.api = apiService;
        this.container = document.getElementById('videoGrid');
        this.sectionTitle = document.getElementById('sectionTitle');
    }

    async load() {
        try {
            const data = await this.api.getRecommendations();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to load recommendations');
            }
            
            StatusBar.updateForModel(data.model_trained, data.total_ratings);
            this.updateTitle(data.model_trained);
            this.displayVideos(data.videos);
            
        } catch (error) {
            console.error('Error loading recommendations:', error);
            this.showError(error.message);
        }
    }

    updateTitle(modelTrained) {
        if (this.sectionTitle) {
            this.sectionTitle.innerHTML = modelTrained
                ? 'AI Recommendations for You <span class="ai-badge">PERSONALIZED</span>'
                : 'Popular Coding Videos <span class="ai-badge">TRENDING</span>';
            this.sectionTitle.style.display = 'flex';
        }
    }

    displayVideos(videos) {
        if (!this.container) return;
        
        if (videos.length === 0) {
            this.container.innerHTML = LoadingState.create(
                'No videos available. Please run the main application to search for videos.',
                false
            );
            return;
        }
        
        this.container.innerHTML = videos.map(video => 
            VideoCard.create(video, {
                showConfidence: true,
                confidenceLabel: 'match'
            })
        ).join('');
    }

    showError(message) {
        if (this.container) {
            this.container.innerHTML = `
                <div class="error">Failed to load recommendations: ${message}</div>
            `;
        }
    }
}

class LikedVideosView {
    constructor(apiService) {
        this.api = apiService;
        this.container = document.getElementById('likedVideoGrid');
        this.sectionTitle = document.getElementById('likedSectionTitle');
        this.addVideoSection = document.getElementById('addVideoSection');
    }

    async load() {
        try {
            const data = await this.api.getLikedVideos();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to load liked videos');
            }
            
            this.displayVideos(data.videos);
            this.updateStatusBar(data.total_liked);
            
        } catch (error) {
            console.error('Error loading liked videos:', error);
            this.showError(error.message);
        }
    }

    displayVideos(videos) {
        // Always show the add video section and title
        if (this.sectionTitle) {
            this.sectionTitle.style.display = 'flex';
        }
        if (this.addVideoSection) {
            this.addVideoSection.style.display = 'block';
        }
        
        if (!this.container) return;
        
        if (videos.length === 0) {
            this.container.innerHTML = LoadingState.create(
                'No videos in MyTube yet. Add videos manually or rate some recommendations!',
                false
            );
            return;
        }
        
        this.container.innerHTML = videos.map(video => 
            VideoCard.create(video, {
                showRemove: true,
                showRating: false,
                showConfidence: true,
                confidenceLabel: 'match',
                cardIdPrefix: 'liked-card-'
            })
        ).join('');
    }

    updateStatusBar(totalLiked) {
        StatusBar.update(
            `🎯 MyTube AI Curation • ${totalLiked} videos I know you'll love • Ranked by confidence`,
            'trained'
        );
    }

    showError(message) {
        if (this.container) {
            this.container.innerHTML = `
                <div class="error">Failed to load liked videos: ${message}</div>
            `;
        }
    }
}

class SearchView {
    constructor(apiService) {
        this.api = apiService;
        this.container = document.getElementById('searchVideoGrid');
        this.header = document.getElementById('searchResultsHeader');
        this.sectionTitle = document.getElementById('searchSectionTitle');
        this.metadata = document.getElementById('searchMetadata');
    }

    showLoading(topic) {
        if (this.container) {
            this.container.innerHTML = `
                <div class="loading" style="grid-column: 1 / -1;">
                    <div class="loading-spinner"></div>
                    <div style="margin-top: 16px;">
                        <div>🤖 Generating search keywords with AI...</div>
                        <div style="margin-top: 8px; font-size: 14px; color: #aaa;">
                            Searching YouTube for "${topic}"
                        </div>
                    </div>
                </div>
            `;
        }
        
        StatusBar.update(
            `🔍 Searching for "${topic}" • Generating keywords with AI • Finding relevant videos`,
            'learning'
        );
    }

    displayResults(result) {
        if (this.header) {
            this.header.style.display = 'block';
        }
        
        if (this.sectionTitle) {
            this.sectionTitle.innerHTML = `
                Search Results for "${result.topic}"
                <span class="ai-badge">AI GENERATED</span>
            `;
        }
        
        if (this.metadata) {
            this.metadata.innerHTML = `
                <div style="display: flex; gap: 20px; flex-wrap: wrap; align-items: center;">
                    <span><strong>${result.total_videos}</strong> videos found</span>
                    <span><strong>${result.keywords_used.length}</strong> AI-generated keywords</span>
                    <span>Session ID: <code style="background: #333; padding: 2px 6px; border-radius: 4px; font-size: 12px;">${result.session_id.substring(0, 8)}...</code></span>
                </div>
                <details style="margin-top: 10px;">
                    <summary style="cursor: pointer; color: #3ea6ff;">View Generated Keywords</summary>
                    <div style="margin-top: 8px; padding: 8px; background: #1a1a1a; border-radius: 6px; font-size: 12px;">
                        ${result.keywords_used.map(keyword => 
                            `<span style="background: #333; padding: 2px 6px; border-radius: 4px; margin: 2px; display: inline-block;">${keyword}</span>`
                        ).join('')}
                    </div>
                </details>
            `;
        }
        
        if (!this.container) return;
        
        if (result.videos.length === 0) {
            this.container.innerHTML = `
                <div class="loading" style="grid-column: 1 / -1;">
                    <div>No videos found for "${result.topic}"</div>
                    <div style="margin-top: 16px;">
                        <button class="nav-btn" onclick="App.clearSearchResults()">Try Another Search</button>
                    </div>
                </div>
            `;
            return;
        }
        
        this.container.innerHTML = result.videos.map(video => 
            VideoCard.create(video, {
                badges: [{
                    text: 'Fresh Search',
                    style: 'background: rgba(0, 212, 170, 0.8); color: white;'
                }]
            })
        ).join('');
        
        StatusBar.update(
            `🎯 Search Complete • Found ${result.total_videos} videos for "${result.topic}" • Using ${result.keywords_used.length} AI keywords`,
            'trained'
        );
    }

    displayError(errorMessage, topic) {
        if (this.header) {
            this.header.style.display = 'block';
        }
        
        if (this.sectionTitle) {
            this.sectionTitle.innerHTML = `
                Search Failed
                <span class="ai-badge" style="background: #ff4444;">ERROR</span>
            `;
        }
        
        if (this.metadata) {
            this.metadata.innerHTML = `
                <div style="color: #ff4444;">
                    Failed to search for "${topic}": ${errorMessage}
                </div>
            `;
        }
        
        if (this.container) {
            this.container.innerHTML = `
                <div class="error" style="grid-column: 1 / -1;">
                    <div style="margin-bottom: 16px;">Search failed: ${errorMessage}</div>
                    <div style="font-size: 14px; color: #aaa; margin-bottom: 16px;">
                        Common issues:
                        <ul style="text-align: left; margin-top: 8px;">
                            <li>YouTube API quota exceeded</li>
                            <li>Ollama service not running</li>
                            <li>Internet connection issues</li>
                            <li>Invalid search topic</li>
                        </ul>
                    </div>
                    <button class="nav-btn" onclick="App.clearSearchResults()">Try Again</button>
                </div>
            `;
        }
    }

    clear() {
        if (this.header) {
            this.header.style.display = 'none';
        }
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

class SearchHistoryView {
    constructor(apiService) {
        this.api = apiService;
        this.container = document.getElementById('searchSessionsList');
        this.sectionTitle = document.getElementById('historySectionTitle');
        this.statsGrid = document.getElementById('statsGrid');
        this.cleanupControls = document.getElementById('cleanupControls');
    }

    async load() {
        try {
            const data = await this.api.getSearchHistory();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to load search history');
            }
            
            this.displayHistory(data.sessions, data.stats);
            this.updateStatusBar(data.sessions.length, data.stats);
            
        } catch (error) {
            console.error('Error loading search history:', error);
            this.showError(error.message);
        }
    }

    displayHistory(sessions, stats) {
        // Show sections
        if (this.sectionTitle) {
            this.sectionTitle.style.display = 'flex';
        }
        if (this.statsGrid) {
            this.statsGrid.style.display = 'grid';
            this.displayStats(stats);
        }
        if (this.cleanupControls) {
            this.cleanupControls.style.display = 'block';
        }
        
        if (!this.container) return;
        
        if (sessions.length === 0) {
            this.container.innerHTML = LoadingState.create(
                'No search sessions found. Search for videos by topic to see them here!',
                false
            );
            return;
        }
        
        this.container.innerHTML = sessions.map(session => 
            SearchSessionCard.create(session)
        ).join('');
    }

    displayStats(stats) {
        if (this.statsGrid) {
            this.statsGrid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-number">${stats.active_sessions}</div>
                    <div class="stat-label">Active Sessions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.search_videos}</div>
                    <div class="stat-label">Videos from Searches</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.recent_sessions}</div>
                    <div class="stat-label">Recent (7 days)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.archived_sessions}</div>
                    <div class="stat-label">Archived Sessions</div>
                </div>
            `;
        }
    }

    displaySessionVideos(videos, topic) {
        if (!this.container) return;
        
        if (videos.length === 0) {
            this.container.innerHTML = `
                <div class="loading">
                    <p>No videos found in this search session.</p>
                    <button class="nav-btn" onclick="App.loadSearchHistory()" style="margin-top: 16px;">
                        ← Back to Search History
                    </button>
                </div>
            `;
            return;
        }
        
        this.container.innerHTML = `
            <div style="margin-bottom: 20px;">
                <button class="nav-btn" onclick="App.loadSearchHistory()" style="margin-bottom: 16px;">
                    ← Back to Search History
                </button>
                <h2 style="color: white; margin-bottom: 20px;">Videos from "${topic}" search</h2>
            </div>
            <div class="video-grid">
                ${videos.map(video => VideoCard.create(video)).join('')}
            </div>
        `;
    }

    updateStatusBar(sessionCount, stats) {
        StatusBar.update(
            `📜 Search History • ${sessionCount} active sessions • ${stats.search_videos} videos from searches`,
            'trained'
        );
    }

    showError(message) {
        if (this.container) {
            this.container.innerHTML = `
                <div class="error">Failed to load search history: ${message}</div>
            `;
        }
    }
}

// Export views for global use
window.RecommendationsView = RecommendationsView;
window.LikedVideosView = LikedVideosView;
window.SearchView = SearchView;
window.SearchHistoryView = SearchHistoryView;