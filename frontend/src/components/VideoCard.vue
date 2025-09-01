<template>
  <div class="video-card">
    <div class="video-thumbnail" @click="openVideo(video.url)">
      <img
        :src="video.thumbnail"
        :alt="video.title"
        @error="handleImageError"
      />
      <div class="confidence-badge" :class="confidenceClass">
        {{ video.confidence }}% match
      </div>
    </div>

    <div class="video-info">
      <div class="video-title" @click="openVideo(video.url)">
        {{ video.title }}
      </div>
      <div class="video-meta">
        <span>{{ video.channel_name }}</span>
        <span>•</span>
        <span>{{ video.views_formatted }}</span>
      </div>

      <div v-if="showRatingButtons" class="rating-buttons">
        <button
          class="rating-btn like-btn"
          :class="{ liked: video.user_rating === true }"
          :disabled="isRating"
          @click="handleRating(true)"
        >
          👍 Like
        </button>
        <button
          class="rating-btn dislike-btn"
          :class="{ disliked: video.user_rating === false }"
          :disabled="isRating"
          @click="handleRating(false)"
        >
          👎 Dislike
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from "vue";
import { openVideo } from "../utils/helpers.js";

export default {
  name: "VideoCard",
  props: {
    video: {
      type: Object,
      required: true,
    },
    showRatingButtons: {
      type: Boolean,
      default: true,
    },
  },
  emits: ["rate-video"],
  setup(props, { emit }) {
    const isRating = ref(false);

    const confidenceClass = computed(() => {
      const confidence = props.video.confidence;
      if (confidence >= 70) return "confidence-high";
      if (confidence >= 40) return "confidence-medium";
      return "confidence-low";
    });

    const handleRating = async (liked) => {
      if (isRating.value) return;

      isRating.value = true;

      try {
        emit("rate-video", {
          videoId: props.video.id,
          liked: liked,
        });
      } finally {
        // Reset rating state after a delay
        setTimeout(() => {
          isRating.value = false;
        }, 1000);
      }
    };

    const handleImageError = (event) => {
      event.target.src =
        "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='320' height='180'><rect width='100%' height='100%' fill='%23333'/><text x='50%' y='50%' text-anchor='middle' dy='.3em' fill='%23999'>No Image</text></svg>";
    };

    return {
      isRating,
      confidenceClass,
      handleRating,
      handleImageError,
      openVideo,
    };
  },
};
</script>
