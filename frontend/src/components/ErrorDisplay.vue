<template>
  <div class="error-state" :class="errorTypeClass">
    <div class="error-icon">{{ errorIcon }}</div>
    <h3>{{ errorTitle }}</h3>
    <p>{{ error }}</p>

    <div class="error-actions">
      <div v-if="errorType === 'quota_exceeded'">
        <p><strong>What you can do:</strong></p>
        <ul>
          <li>Wait for quota to reset (happens daily)</li>
          <li>Try again tomorrow</li>
          <li>Use a different YouTube API key if available</li>
        </ul>
      </div>

      <div v-else-if="errorType === 'invalid_api_key'">
        <p><strong>How to fix:</strong></p>
        <ul>
          <li>Check your .env file has the correct YOUTUBE_API_KEY</li>
          <li>
            Get a new API key from
            <a href="https://console.developers.google.com/" target="_blank"
              >Google Cloud Console</a
            >
          </li>
          <li>Make sure the YouTube Data API v3 is enabled</li>
        </ul>
      </div>

      <div v-else-if="errorType === 'network_error'">
        <p><strong>Try these steps:</strong></p>
        <ul>
          <li>Check your internet connection</li>
          <li>Refresh the page</li>
          <li>Try again in a few moments</li>
        </ul>
      </div>

      <button @click="$emit('retry')" class="retry-btn">
        {{ errorType === "network_error" ? "Refresh Page" : "Retry" }}
      </button>
    </div>
  </div>
</template>

<script>
import { computed } from "vue";
import { parseErrorType } from "../utils/helpers.js";

export default {
  name: "ErrorDisplay",
  props: {
    error: {
      type: String,
      required: true,
    },
  },
  emits: ["retry"],
  setup(props) {
    const errorType = computed(() => parseErrorType(props.error));

    const errorTypeClass = computed(() => {
      switch (errorType.value) {
        case "quota_exceeded":
          return "quota-error";
        case "invalid_api_key":
          return "api-error";
        case "network_error":
          return "network-error";
        default:
          return "";
      }
    });

    const errorIcon = computed(() => {
      switch (errorType.value) {
        case "quota_exceeded":
          return "⚠️";
        case "invalid_api_key":
          return "🔑";
        case "network_error":
          return "🌐";
        default:
          return "❌";
      }
    });

    const errorTitle = computed(() => {
      switch (errorType.value) {
        case "quota_exceeded":
          return "YouTube API Quota Exceeded";
        case "invalid_api_key":
          return "Invalid API Key";
        case "network_error":
          return "Network Error";
        default:
          return "Something went wrong";
      }
    });

    return {
      errorType,
      errorTypeClass,
      errorIcon,
      errorTitle,
    };
  },
};
</script>
