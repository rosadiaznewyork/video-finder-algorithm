"""
Ollama integration for generating YouTube search keywords from topics.
"""

import os
import json
import requests
import random
from typing import List, Optional

from src.config.app_config import OllamaConfig, YouTubeConfig


def check_ollama_running() -> bool:
    """Check if Ollama service is running."""
    try:
        response = requests.get(OllamaConfig.TAGS_ENDPOINT, timeout=2)
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        return False


def get_model_from_env() -> str:
    """Get Ollama model from environment variable."""
    return OllamaConfig.get_model_from_env()


def check_model_exists(model: str) -> bool:
    """Check if specified model is available in Ollama."""
    try:
        response = requests.get(OllamaConfig.TAGS_ENDPOINT, timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return any(m['name'] == model for m in models)
    except (requests.ConnectionError, requests.Timeout, KeyError):
        return False
    return False


def list_available_models() -> List[str]:
    """List all available Ollama models."""
    try:
        response = requests.get(OllamaConfig.TAGS_ENDPOINT, timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return [m['name'] for m in models]
    except (requests.ConnectionError, requests.Timeout, KeyError):
        return []
    return []


def generate_keywords_from_topic(topic: str, num_queries: int = None) -> Optional[List[str]]:
    """
    Generate YouTube search keywords from a topic using Ollama.
    
    Args:
        topic: The topic to generate keywords for
        num_queries: Number of search queries to generate (uses default if None)
        
    Returns:
        List of search queries or None if error
    """
    if num_queries is None:
        num_queries = OllamaConfig.DEFAULT_NUM_QUERIES
        
    if not check_ollama_running():
        print("Error: Ollama service is not running.")
        print("Please start Ollama with: ollama serve")
        return None
    
    model = get_model_from_env()
    
    if not check_model_exists(model):
        print(f"Error: Model '{model}' not found.")
        available = list_available_models()
        if available:
            print(f"Available models: {', '.join(available)}")
        else:
            print(f"No models found. Please pull a model with: ollama pull {OllamaConfig.DEFAULT_MODEL}")
        return None
    
    prompt = f"""Generate {num_queries} YouTube search queries for finding programming/coding videos about: {topic}

Create diverse queries including:
- Simple topic names (e.g., just "{topic}")
- Basic combinations (e.g., "{topic} tutorial")
- Broader terms without too many keywords
- Some project-based queries
- Avoid overly specific or long queries

Make queries natural and broad enough to find popular videos.
Keep queries concise - most should be 2-4 words.

Return only the search queries, one per line. Do not include numbering or bullet points."""
    
    try:
        response = requests.post(
            OllamaConfig.GENERATE_ENDPOINT,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=OllamaConfig.REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')
            
            # Parse the response into individual queries
            queries = [
                line.strip() 
                for line in response_text.split('\n') 
                if line.strip() and not line.strip().startswith(('-', '*', '•'))
            ]
            
            # Remove any numbering (e.g., "1.", "2.") at the start of queries
            cleaned_queries = []
            for query in queries:
                # Remove leading numbers and dots
                if query and query[0].isdigit():
                    query = query.lstrip('0123456789.)').strip()
                if query:
                    cleaned_queries.append(query)
            
            return cleaned_queries[:num_queries]
        else:
            print(f"Error: Ollama API returned status {response.status_code}")
            return None
            
    except requests.Timeout:
        print("Error: Ollama request timed out. The model may be loading or slow.")
        return None
    except requests.ConnectionError:
        print("Error: Could not connect to Ollama service.")
        return None
    except Exception as e:
        print(f"Error generating keywords: {str(e)}")
        return None


def fallback_manual_keywords(topic: str) -> List[str]:
    """
    Fallback method to generate basic keywords without Ollama.
    
    Args:
        topic: The topic to generate keywords for
        
    Returns:
        List of basic search queries
    """
    # More generic patterns that work better with YouTube API
    patterns = [
        topic,  # Just the topic itself
        f"{topic} tutorial",
        f"{topic} course",
        f"{topic} programming",
        f"{topic} coding",
        f"{topic} project",
        f"learn {topic}",
        f"{topic} basics",
        f"{topic} advanced",
        f"{topic} tips",
        f"best {topic}",
        f"{topic} guide",
        f"{topic} example",
        f"{topic} explained",
        f"how to {topic}"
    ]
    
    return patterns


def generate_default_coding_queries(num_queries: int = None, db_path: str = None) -> Optional[List[str]]:
    """
    Generate default coding search queries using dynamic prompts with personalized keywords.
    
    Args:
        num_queries: Number of search queries to generate (uses default if None)
        db_path: Database path for personalized keywords (required for personalization)
        
    Returns:
        List of search queries or None if error
    """
    if num_queries is None:
        num_queries = OllamaConfig.DEFAULT_NUM_QUERIES
        
    if not check_ollama_running():
        print("Error: Ollama service is not running.")
        print("Please start Ollama with: ollama serve")
        return None
    
    model = get_model_from_env()
    
    if not check_model_exists(model):
        print(f"Error: Model '{model}' not found.")
        available = list_available_models()
        if available:
            print(f"Available models: {', '.join(available)}")
        else:
            print(f"No models found. Please pull a model with: ollama pull {OllamaConfig.DEFAULT_MODEL}")
        return None
    
    # Get personalized keywords based on liked videos or fallback to static keywords
    if db_path:
        from src.services.tag_service import TagService
        tag_service = TagService(db_path)
        selected_keywords = tag_service.get_personalized_keywords(random.randint(8, 10))
        keyword_source = tag_service.get_keyword_source()
        print(f"🎯 Using {keyword_source}")
    else:
        # Fallback to static programming keywords if no db_path provided
        selected_keywords = random.sample(
            YouTubeConfig.PROGRAMMING_KEYWORDS, 
            min(random.randint(8, 10), len(YouTubeConfig.PROGRAMMING_KEYWORDS))
        )
        print("🔧 Using fallback static programming keywords")
    
    keywords_str = ", ".join(selected_keywords)
    
    prompt = f"""Generate {num_queries} YouTube search queries for finding programming/coding videos focused on practical projects and development.

Focus on these technology areas and concepts: {keywords_str}

Create diverse queries that emphasize:
- Building real projects and applications
- Practical development tutorials
- Project-focused learning
- Technology implementation
- Development workflows and best practices

Make queries natural and broad enough to find popular project-oriented videos.
Keep queries concise - most should be 2-4 words.
Focus on "building", "creating", "developing" rather than basic tutorials.

Examples of good queries: "build web app", "react project tutorial", "python automation project"

Return only the search queries, one per line. Do not include numbering or bullet points."""
    
    try:
        response = requests.post(
            OllamaConfig.GENERATE_ENDPOINT,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=OllamaConfig.REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')
            
            # Parse the response into individual queries
            queries = [
                line.strip() 
                for line in response_text.split('\n') 
                if line.strip() and not line.strip().startswith(('-', '*', '•'))
            ]
            
            # Remove any numbering (e.g., "1.", "2.") at the start of queries
            cleaned_queries = []
            for query in queries:
                # Remove leading numbers and dots
                if query and query[0].isdigit():
                    query = query.lstrip('0123456789.)').strip()
                if query:
                    cleaned_queries.append(query)
            
            return cleaned_queries[:num_queries]
        else:
            print(f"Error: Ollama API returned status {response.status_code}")
            return None
            
    except requests.Timeout:
        print("Error: Ollama request timed out. The model may be loading or slow.")
        return None
    except requests.ConnectionError:
        print("Error: Could not connect to Ollama service.")
        return None
    except Exception as e:
        print(f"Error generating queries: {str(e)}")
        return None


if __name__ == "__main__":
    # Test the module
    print("Testing Ollama integration...")
    
    if check_ollama_running():
        print("✓ Ollama is running")
        
        model = get_model_from_env()
        print(f"Using model: {model}")
        
        if check_model_exists(model):
            print(f"✓ Model {model} is available")
            
            # Test keyword generation
            test_topic = "rust web development"
            print(f"\nGenerating keywords for topic: {test_topic}")
            keywords = generate_keywords_from_topic(test_topic, 5)
            
            if keywords:
                print("\nGenerated keywords:")
                for i, keyword in enumerate(keywords, 1):
                    print(f"  {i}. {keyword}")
            else:
                print("Failed to generate keywords")
        else:
            print(f"✗ Model {model} not found")
            available = list_available_models()
            if available:
                print(f"Available models: {', '.join(available)}")
    else:
        print("✗ Ollama is not running")
        print("Please start Ollama with: ollama serve")
        
        # Test fallback
        print("\nTesting fallback keyword generation...")
        fallback = fallback_manual_keywords("python web scraping")
        print("Fallback keywords:")
        for i, keyword in enumerate(fallback[:5], 1):
            print(f"  {i}. {keyword}")