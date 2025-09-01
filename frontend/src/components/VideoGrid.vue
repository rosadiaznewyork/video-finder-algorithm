<template>
  <div class="video-grid-container">
    <!-- Empty State -->
    <div v-if="videos.length === 0" class="empty-state">
      <div class="empty-icon">📺</div>
      <h3>No videos available</h3>
      <p>The app should automatically load videos on startup.</p>
      <div class="empty-actions">
        <p>If this persists, try running: <code>python app.py search</code></p>
        <button @click="$emit('retry')" class="retry-btn">Refresh</button>
      </div>
    </div>

    <!-- Video Grid -->
    <div v-else class="video-grid">
      <VideoCard
        v-for="video in videos"
        :key="video.id"
        :video="video"
        :show-rating-buttons="showRatingButtons"
        @rate-video="$emit('rate-video', $event.videoId, $event.liked)"
      />
    </div>
  </div>
</template>

<script>
import VideoCard from './VideoCard.vue'

export default {
  name: 'VideoGrid',
  components: {
    VideoCard
  },
  props: {
    videos: {
      type: Array,
      default: () => []
    },
    showRatingButtons: {
      type: Boolean,
      default: true
    }
  },
  emits: ['rate-video', 'retry']
}
</script>
