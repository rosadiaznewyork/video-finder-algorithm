"""
YouTube API Service
Handles all YouTube API interactions including search, video details, and utilities
"""
import requests
import json
import re
from typing import List, Dict

class YouTubeService:
    """Service for interacting with YouTube API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def search_videos(self, query: str, max_results: int = 10) -> List[str]:
        """Search for videos and return video IDs"""
        search_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'key': self.api_key,
            'q': query,
            'part': 'snippet',
            'type': 'video',
            'order': 'viewCount',
            'maxResults': max_results,
            'publishedAfter': '2020-01-01T00:00:00Z'
        }

        try:
            response = requests.get(search_url, params=params)
            data = response.json()

            # Check for API errors
            if 'error' in data:
                error_msg = data['error'].get('message', 'Unknown error')
                if 'quota' in error_msg.lower():
                    print(f"⚠️  YouTube API quota exceeded for query '{query}'")
                else:
                    print(f"YouTube API Error for '{query}': {error_msg}")
                return []

            if 'items' not in data:
                return []

            video_ids = [item['id']['videoId'] for item in data['items']]
            return video_ids

        except Exception as e:
            print(f"Error searching videos for '{query}': {e}")
            return []
    
    def get_video_details(self, video_ids: List[str]) -> List[Dict]:
        """Get detailed information for a list of video IDs"""
        if not video_ids:
            return []

        details_url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'key': self.api_key,
            'id': ','.join(video_ids),
            'part': 'snippet,statistics,contentDetails'
        }

        try:
            response = requests.get(details_url, params=params)
            data = response.json()

            videos = []
            for item in data.get('items', []):
                video = self._parse_video_response(item)
                if self._is_relevant_video(video):
                    videos.append(video)

            return videos

        except Exception as e:
            print(f"Error getting video details: {e}")
            return []
    
    def search_and_get_details(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for videos and get their details in one call"""
        video_ids = self.search_videos(query, max_results)
        return self.get_video_details(video_ids)
    
    def _parse_video_response(self, item: Dict) -> Dict:
        """Parse YouTube API response into our video format"""
        snippet = item['snippet']
        statistics = item['statistics']

        return {
            'id': item['id'],
            'title': snippet['title'],
            'description': snippet['description'],
            'view_count': int(statistics.get('viewCount', 0)),
            'like_count': int(statistics.get('likeCount', 0)),
            'comment_count': int(statistics.get('commentCount', 0)),
            'duration': item['contentDetails']['duration'],
            'published_at': snippet['publishedAt'],
            'channel_name': snippet['channelTitle'],
            'thumbnail_url': snippet['thumbnails']['high']['url'],
            'tags': json.dumps(snippet.get('tags', [])),
            'category_id': int(snippet.get('categoryId', 0)),
            'url': f"https://www.youtube.com/watch?v={item['id']}"
        }
    
    def _is_relevant_video(self, video: Dict) -> bool:
        """Filter videos based on general quality criteria"""
        # Basic quality filters - no content-specific bias
        if video['view_count'] < 10000:  # Lowered threshold for broader content
            return False

        # Filter out very short videos (likely not substantial content)
        duration = video.get('duration', '')
        if 'PT' in duration:
            # Parse ISO 8601 duration format (PT1M30S = 1 minute 30 seconds)
            minutes = re.findall(r'(\d+)M', duration)
            seconds = re.findall(r'(\d+)S', duration)
            total_seconds = (int(minutes[0]) * 60 if minutes else 0) + (int(seconds[0]) if seconds else 0)
            if total_seconds < 60:  # Skip videos under 1 minute
                return False

        return True
    
    @staticmethod
    def remove_duplicate_videos(videos: List[Dict]) -> List[Dict]:
        """Remove duplicate videos from a list"""
        seen_ids = set()
        unique_videos = []

        for video in videos:
            if video['id'] not in seen_ids:
                seen_ids.add(video['id'])
                unique_videos.append(video)

        return unique_videos


# Backward compatibility functions (for existing code)
def search_youtube_videos_by_query(api_key: str, query: str, max_results: int) -> List[str]:
    """Backward compatibility wrapper"""
    service = YouTubeService(api_key)
    return service.search_videos(query, max_results)

def get_video_details_from_youtube(api_key: str, video_ids: List[str]) -> List[Dict]:
    """Backward compatibility wrapper"""
    service = YouTubeService(api_key)
    return service.get_video_details(video_ids)

def remove_duplicate_videos(videos: List[Dict]) -> List[Dict]:
    """Backward compatibility wrapper"""
    return YouTubeService.remove_duplicate_videos(videos)
