<template>
  <div class="status-bar">
    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      {{ loadingMessage }}
    </div>
    
    <!-- Error State -->
    <div v-else-if="error" class="error">
      ❌ {{ error }}
    </div>
    
    <!-- Rating View Status -->
    <div v-else-if="currentView === 'rating'" class="status-content">
      <div v-if="modelTrained" class="status-trained">
        🤖 AI Model Active • Trained on {{ totalRatings }} video ratings • Showing personalized recommendations
      </div>
      <div v-else class="status-learning">
        📚 Learning Mode • Need {{ Math.max(0, 3 - totalRatings) }} more ratings to activate AI recommendations
      </div>
    </div>
    
    <!-- Liked View Status -->
    <div v-else-if="currentView === 'liked'" class="status-content">
      <div class="status-trained">
        🎯 MyTube AI Curation • {{ totalLiked }} videos I know you'll love • Ranked by confidence
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'StatusBar',
  props: {
    modelTrained: {
      type: Boolean,
      default: false
    },
    totalRatings: {
      type: Number,
      default: 0
    },
    totalLiked: {
      type: Number,
      default: 0
    },
    currentView: {
      type: String,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: null
    }
  },
  setup(props) {
    const loadingMessage = computed(() => {
      if (props.currentView === 'liked') {
        return 'Loading your curated videos...'
      }
      return 'Loading your personalized recommendations...'
    })

    return {
      loadingMessage
    }
  }
}
</script>
