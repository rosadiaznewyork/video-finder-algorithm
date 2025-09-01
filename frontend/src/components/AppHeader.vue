<template>
  <header class="header">
    <div class="logo-section">
      <a href="/" class="logo">
        <div class="logo-icon">VI</div>
        <span class="logo-text">Video Inspiration</span>
      </a>
    </div>

    <div class="search-container">
      <input
        type="text"
        class="search-box"
        placeholder="Search coding videos..."
        disabled
      />
      <button class="search-button">🔍</button>
    </div>

    <div class="nav-buttons">
      <button
        class="nav-btn"
        :class="{ active: currentView === 'rating' }"
        @click="$emit('view-change', 'rating')"
      >
        📝 Rate Videos
      </button>
      <button
        class="nav-btn"
        :class="{ active: currentView === 'liked' }"
        @click="$emit('view-change', 'liked')"
      >
        🎯 MyTube
      </button>
    </div>
  </header>
</template>

<script>
export default {
  name: 'AppHeader',
  props: {
    currentView: {
      type: String,
      required: true
    }
  },
  emits: ['view-change']
}
</script>
