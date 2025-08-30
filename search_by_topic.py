#!/usr/bin/env python3
"""
Search for YouTube videos based on user-provided topics using Ollama LLMs.

Refactored to use new service architecture for cleaner code.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

from src.services.video_search_service import TopicVideoSearchService
from src.ollama.keyword_generator import (
    generate_keywords_from_topic, 
    fallback_manual_keywords,
    check_ollama_running
)
from src.config.app_config import AppConfig


def search_videos_by_topic(topic: str, use_fallback: bool = False) -> None:
    """
    Search for videos based on a topic by generating relevant keywords.
    
    Args:
        topic: The topic to search for
        use_fallback: Use fallback keyword generation instead of Ollama
    """
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found in environment variables")
        return

    # Use the new service architecture
    search_service = TopicVideoSearchService(api_key)
    
    # Generate search keywords
    if use_fallback:
        print("📝 Using fallback keyword generation...")
        keywords = fallback_manual_keywords(topic)
    else:
        print("🤖 Generating search keywords with Ollama...")
        keywords = generate_keywords_from_topic(topic, num_queries=15)
        
        if not keywords:
            print("⚠️  Falling back to manual keyword generation...")
            keywords = fallback_manual_keywords(topic)
    
    if not keywords:
        print("❌ Could not generate keywords for this topic.")
        return
    
    print(f"\n📋 Generated {len(keywords)} search queries:")
    for i, keyword in enumerate(keywords[:5], 1):  # Show first 5
        print(f"   {i}. {keyword}")
    if len(keywords) > 5:
        print(f"   ... and {len(keywords) - 5} more")
    
    # Use the service to search and save videos
    unique_videos = search_service.search_topic_with_keywords(topic, keywords)
    
    if unique_videos:
        print(f"\n✅ Successfully saved {len(unique_videos)} unique videos!")
        print("\n🎬 Sample videos found:")
        for video in unique_videos[:3]:
            title = video['title'][:70] + "..." if len(video['title']) > 70 else video['title']
            print(f"  • {title}")
            print(f"    Channel: {video['channel_name']}")
            print(f"    Views: {video['view_count']:,}")
            print()
    else:
        print("\n❌ No unique videos found for this topic.")
    
    print("🏁 Search complete!")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Search YouTube videos by topic using AI-generated keywords"
    )
    parser.add_argument(
        "--topic", 
        "-t",
        type=str, 
        help="The topic to search for"
    )
    parser.add_argument(
        "--fallback",
        "-f",
        action="store_true",
        help="Use fallback keyword generation (no Ollama required)"
    )
    
    args = parser.parse_args()
    
    load_dotenv()
    
    # Get topic from args or interactive input
    if args.topic:
        topic = args.topic
    else:
        print("\n🎯 YouTube Video Search by Topic")
        print("=" * 40)
        
        if not args.fallback:
            # Check Ollama status
            if check_ollama_running():
                print("✅ Ollama is running")
            else:
                print("⚠️  Ollama is not running")
                print("   To use AI keyword generation, start Ollama with:")
                print("   $ ollama serve")
                print("\n   Or use --fallback flag for basic keyword generation")
                response = input("\nContinue with fallback mode? (y/n): ")
                if response.lower() != 'y':
                    print("Exiting...")
                    sys.exit(0)
                args.fallback = True
        
        topic = input("\n📝 Enter topic to search for: ").strip()
        
        if not topic:
            print("❌ Topic cannot be empty")
            sys.exit(1)
    
    # Run the search
    search_videos_by_topic(topic, use_fallback=args.fallback)


if __name__ == "__main__":
    main()