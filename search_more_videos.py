#!/usr/bin/env python3
import os
from dotenv import load_dotenv

from src.config.app_config import AppConfig
from src.services.video_search_service import VideoSearchService
from src.services.query_service import QueryService

load_dotenv()

def search_more_videos():
    """Search for additional coding videos using the VideoSearchService."""
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found in environment variables")
        return

    print("🔍 Searching for more coding videos...")

    # Use QueryService to get AI-generated additional queries with database path for personalization
    query_service = QueryService(AppConfig.DATABASE_PATH)
    additional_queries = query_service.get_additional_queries(
        use_ai=True, 
        num_queries=10
    )
    
    if additional_queries:
        print(f"🤖 Generated {len(additional_queries)} search queries using AI")
    else:
        print("⚠️ Using fallback queries")

    # Use VideoSearchService for clean, unified search
    search_service = VideoSearchService(api_key, AppConfig.DATABASE_PATH)
    unique_videos = search_service.search_and_save_videos(
        queries=additional_queries,
        max_results_per_query=AppConfig.DEFAULT_RESULTS_PER_QUERY
    )

    if unique_videos:
        print(f"✅ Found and saved {len(unique_videos)} new videos!")
    else:
        print("❌ No new videos found.")

if __name__ == "__main__":
    search_more_videos()