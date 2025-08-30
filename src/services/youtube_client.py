"""
Unified YouTube API client with consistent error handling.
"""

import requests
from typing import List, Dict, Optional

from src.config.app_config import YouTubeConfig


class YouTubeAPIClient:
    """Unified client for YouTube API operations with consistent error handling."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def search_videos(self, query: str, max_results: int = 10) -> List[str]:
        """
        Search for video IDs using the YouTube API.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of video IDs
        """
        params = {
            'key': self.api_key,
            'q': query,
            'part': 'snippet',
            'type': 'video',
            'order': 'viewCount',
            'maxResults': max_results,
            'videoCategoryId': YouTubeConfig.SCIENCE_TECH_CATEGORY_ID,
            'publishedAfter': YouTubeConfig.DEFAULT_PUBLISHED_AFTER
        }
        
        response_data = self._make_request(YouTubeConfig.BASE_SEARCH_URL, params)
        if not response_data:
            return []
            
        # Check if we have items
        if 'items' not in response_data:
            print(f"       - No 'items' in response")
            if 'pageInfo' in response_data:
                total_results = response_data['pageInfo'].get('totalResults', 0)
                print(f"       - Total results available: {total_results}")
            return []

        if len(response_data['items']) == 0:
            print(f"       - Empty results for query")
            return []

        video_ids = [item['id']['videoId'] for item in response_data['items']]
        return video_ids
    
    def get_video_details(self, video_ids: List[str]) -> List[Dict]:
        """
        Get detailed information for a list of video IDs.
        
        Args:
            video_ids: List of YouTube video IDs
            
        Returns:
            List of video detail dictionaries
        """
        if not video_ids:
            return []

        params = {
            'key': self.api_key,
            'id': ','.join(video_ids),
            'part': 'snippet,statistics,contentDetails'
        }

        response_data = self._make_request(YouTubeConfig.BASE_DETAILS_URL, params)
        if not response_data:
            return []

        if 'items' not in response_data:
            print(f"       ✗ No video details returned for {len(video_ids)} video IDs")
            return []

        items = response_data.get('items', [])
        print(f"       → Processing {len(items)} video details...")
        
        videos = []
        for i, item in enumerate(items):
            try:
                video = self._parse_video_response(item) 
                videos.append(video)
            except Exception as e:
                print(f"       ✗ Error parsing video {i+1}: {type(e).__name__}: {e}")
                continue

        print(f"       → {len(videos)} videos passed relevance filter")
        return videos
    
    def test_connection(self) -> bool:
        """
        Test if the API key and connection are working.
        
        Returns:
            True if connection is working, False otherwise
        """
        try:
            result = self.search_videos("test", 1)
            return True  # If no exception, API is working
        except:
            return False
    
    def _make_request(self, url: str, params: dict) -> Optional[dict]:
        """
        Make a request to the YouTube API with unified error handling.
        
        Args:
            url: API endpoint URL
            params: Request parameters
            
        Returns:
            Response data dictionary or None if error
        """
        try:
            response = requests.get(url, params=params, timeout=YouTubeConfig.REQUEST_TIMEOUT)
            return self._handle_response(response)
            
        except requests.Timeout:
            print(f"       ✗ Request timeout after {YouTubeConfig.REQUEST_TIMEOUT} seconds")
            return None
        except requests.ConnectionError:
            print(f"       ✗ Connection error - check internet connection")
            return None
        except Exception as e:
            print(f"       ✗ Unexpected error: {type(e).__name__}: {e}")
            return None
    
    def _handle_response(self, response: requests.Response) -> Optional[dict]:
        """
        Handle API response with consistent error reporting.
        
        Args:
            response: HTTP response object
            
        Returns:
            Response data dictionary or None if error
        """
        # Check HTTP status code
        if response.status_code != 200:
            print(f"       ✗ HTTP {response.status_code}: {response.reason}")
            if response.status_code == 403:
                print(f"       ✗ API quota exceeded or invalid key")
            elif response.status_code == 400:
                print(f"       ✗ Bad request - check API parameters")
            
            # Try to get detailed error info
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_info = error_data['error']
                    print(f"       ✗ {error_info.get('message', 'Unknown error')}")
                    if 'errors' in error_info:
                        for err in error_info['errors']:
                            print(f"       ✗ {err.get('reason', '')}: {err.get('message', '')}")
            except:
                print(f"       ✗ Response: {response.text[:200]}")
            
            return None

        # Parse JSON response
        try:
            data = response.json()
        except ValueError as e:
            print(f"       ✗ Invalid JSON response: {e}")
            return None
        
        # Check for API errors in response
        if 'error' in data:
            error_info = data['error']
            print(f"       ✗ API Error: {error_info.get('message', 'Unknown error')}")
            if error_info.get('code') == 403:
                print(f"       ✗ Quota exceeded or permission denied")
            return None

        return data
    
    def _parse_video_response(self, item: dict) -> dict:
        """
        Parse a video item from the YouTube API response.
        
        Args:
            item: Video item from API response
            
        Returns:
            Parsed video dictionary
        """
        import json
        
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
