#!/usr/bin/env python3
"""
Search for YouTube videos on a topic and immediately rate them.
Combines topic-based search with interactive rating session.

Refactored to use new service architecture for cleaner code.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

from src.services.topic_rating_service import TopicRatingService, MultiTopicRatingService
from src.ollama.keyword_generator import check_ollama_running
from src.config.app_config import AppConfig


def main():
    """Main entry point for topic-based rating."""
    parser = argparse.ArgumentParser(
        description="Search for videos on a topic and rate them immediately"
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
    parser.add_argument(
        "--continuous",
        "-c",
        action="store_true",
        help="Continue with multiple topics"
    )
    
    args = parser.parse_args()
    
    load_dotenv()
    
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found in environment variables")
        return
    
    # Check Ollama status if not using fallback
    if not args.fallback and not check_ollama_running():
        print("⚠️  Ollama is not running")
        print("   To use AI keyword generation, start Ollama with:")
        print("   $ ollama serve")
        print("\n   Or use --fallback flag for basic keyword generation")
        response = input("\nContinue with fallback mode? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(0)
        args.fallback = True
    
    # Handle single topic or continuous mode
    if args.continuous:
        # Continuous mode - multiple topics
        service = MultiTopicRatingService(api_key)
        service.run_continuous_rating_sessions(use_fallback=args.fallback)
    else:
        # Single topic mode
        service = TopicRatingService(api_key)
        
        if args.topic:
            topic = args.topic
        else:
            topic = input("\n📝 Enter topic to search and rate: ").strip()
            
            if not topic:
                print("❌ Topic cannot be empty")
                sys.exit(1)
        
        # Run single topic rating session
        rated_count = service.run_rating_session_for_topic(topic, use_fallback=args.fallback)
        
        if rated_count > 0:
            print(f"\n🎯 Rated {rated_count} videos for '{topic}'")
        else:
            print("\n❌ No videos were rated.")


if __name__ == "__main__":
    main()