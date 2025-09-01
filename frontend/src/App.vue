<template>
  <div class="app">
    <AppHeader :current-view="currentView" @view-change="handleViewChange" />

    <StatusBar
      :model-trained="modelTrained"
      :total-ratings="totalRatings"
      :total-liked="totalLiked"
      :current-view="currentView"
      :loading="loading"
      :error="error"
    />

    <main class="main-content">
      <!-- Rating View -->
      <div v-if="currentView === 'rating'" class="view-container active">
        <h1 v-if="!loading && !error" class="section-title">
          {{
            modelTrained
              ? "AI Recommendations for You"
              : "Popular Coding Videos"
          }}
          <span class="ai-badge">{{
            modelTrained ? "PERSONALIZED" : "TRENDING"
          }}</span>
        </h1>

        <ErrorDisplay
          v-if="error && currentView === 'rating'"
          :error="error"
          @retry="loadRecommendations"
        />

        <VideoGrid
          v-else-if="!loading"
          :videos="videos"
          :show-rating-buttons="true"
          @rate-video="handleRateVideo"
        />
      </div>

      <!-- Liked Videos View -->
      <div v-if="currentView === 'liked'" class="view-container active">
        <h1 v-if="likedVideos.length > 0" class="section-title">
          MyTube - Videos I Know You'll Love
          <span class="ai-badge">AI CURATED</span>
        </h1>

        <ErrorDisplay
          v-if="error && currentView === 'liked'"
          :error="error"
          @retry="loadLikedVideos"
        />

        <VideoGrid
          v-else-if="!loading"
          :videos="likedVideos"
          :show-rating-buttons="false"
        />

        <div v-if="!loading && likedVideos.length === 0" class="loading">
          No videos curated yet. Rate some videos and I'll learn what you love!
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from "vue";
import AppHeader from "./components/AppHeader.vue";
import StatusBar from "./components/StatusBar.vue";
import VideoGrid from "./components/VideoGrid.vue";
import ErrorDisplay from "./components/ErrorDisplay.vue";
import {
  fetchRecommendations,
  fetchLikedVideos,
  rateVideo,
} from "./api/videos.js";
import { showNotification } from "./utils/notifications.js";

export default {
  name: "App",
  components: {
    AppHeader,
    StatusBar,
    VideoGrid,
    ErrorDisplay,
  },
  setup() {
    // Reactive state
    const currentView = ref("rating");
    const loading = ref(false);
    const error = ref(null);

    // Video data
    const videos = ref([]);
    const likedVideos = ref([]);

    // Model state
    const modelTrained = ref(false);
    const totalRatings = ref(0);
    const totalLiked = ref(0);

    // Auto-refresh interval
    let refreshInterval = null;

    // Methods
    const handleViewChange = (view) => {
      currentView.value = view;
      error.value = null;

      if (view === "rating") {
        loadRecommendations();
      } else if (view === "liked") {
        loadLikedVideos();
      }
    };

    const loadRecommendations = async () => {
      try {
        loading.value = true;
        error.value = null;

        const data = await fetchRecommendations();

        videos.value = data.videos;
        modelTrained.value = data.model_trained;
        totalRatings.value = data.total_ratings;
      } catch (err) {
        console.error("Error loading recommendations:", err);
        error.value = err.message;
      } finally {
        loading.value = false;
      }
    };

    const loadLikedVideos = async () => {
      try {
        loading.value = true;
        error.value = null;

        const data = await fetchLikedVideos();

        likedVideos.value = data.videos;
        totalLiked.value = data.total_liked;
      } catch (err) {
        console.error("Error loading liked videos:", err);
        error.value = err.message;
      } finally {
        loading.value = false;
      }
    };

    const handleRateVideo = async (videoId, liked) => {
      try {
        const result = await rateVideo(videoId, liked);

        // Show success notification
        const action = liked ? "liked" : "disliked";
        showNotification(
          `Video ${action}! ${
            result.model_retrained ? "AI model updated." : ""
          }`,
          "success"
        );

        // Refresh current view if model was retrained
        if (result.model_retrained) {
          setTimeout(() => {
            if (currentView.value === "rating") {
              loadRecommendations();
            }
          }, 1000);
        }
      } catch (err) {
        console.error("Error rating video:", err);
        showNotification(`Failed to rate video: ${err.message}`, "error");
      }
    };

    const setupAutoRefresh = () => {
      // Clear existing interval
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }

      // Refresh current view every 5 minutes
      refreshInterval = setInterval(() => {
        if (currentView.value === "rating") {
          loadRecommendations();
        } else if (currentView.value === "liked") {
          loadLikedVideos();
        }
      }, 300000); // 5 minutes
    };

    // Lifecycle hooks
    onMounted(() => {
      loadRecommendations();
      setupAutoRefresh();
    });

    onUnmounted(() => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    });

    return {
      currentView,
      loading,
      error,
      videos,
      likedVideos,
      modelTrained,
      totalRatings,
      totalLiked,
      handleViewChange,
      loadRecommendations,
      loadLikedVideos,
      handleRateVideo,
    };
  },
};
</script>
