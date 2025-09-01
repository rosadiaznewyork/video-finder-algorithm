/**
 * API module for video-related operations
 */

/**
 * Fetch video recommendations from the API
 * @returns {Promise<Object>} API response with recommendations
 */
export async function fetchRecommendations() {
  const response = await fetch('/api/recommendations');
  const data = await response.json();
  
  if (!data.success) {
    throw new Error(data.error || 'Failed to load recommendations');
  }
  
  return data;
}

/**
 * Fetch liked videos from the API
 * @returns {Promise<Object>} API response with liked videos
 */
export async function fetchLikedVideos() {
  const response = await fetch('/api/liked');
  const data = await response.json();
  
  if (!data.success) {
    throw new Error(data.error || 'Failed to load liked videos');
  }
  
  return data;
}

/**
 * Rate a video (like or dislike)
 * @param {string} videoId - The video ID to rate
 * @param {boolean} liked - Whether the video was liked (true) or disliked (false)
 * @returns {Promise<Object>} API response with rating result
 */
export async function rateVideo(videoId, liked) {
  const response = await fetch('/api/rate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      video_id: videoId,
      liked: liked
    })
  });
  
  const data = await response.json();
  
  if (!data.success) {
    throw new Error(data.error || 'Failed to rate video');
  }
  
  return data;
}
