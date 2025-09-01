import json
import os
from typing import List
from pathlib import Path

def get_config_path() -> str:
    """Get the path to the search queries configuration file."""
    # Get the project root directory (where main.py is located)
    project_root = Path(__file__).parent.parent.parent
    return str(project_root / "config" / "search_queries.json")

def load_search_queries() -> dict:
    """Load search queries from the configuration file."""
    config_path = get_config_path()
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Search queries config file not found at {config_path}")
        print("Using default fallback queries.")
        return get_default_queries()
    except json.JSONDecodeError as e:
        print(f"Error parsing search queries config: {e}")
        print("Using default fallback queries.")
        return get_default_queries()

def get_default_queries() -> dict:
    """Fallback queries if config file is missing or invalid."""
    return {
        "search_queries": [
            "tutorial",
            "how to",
            "guide",
            "tips",
            "review",
            "explained",
            "basics",
            "beginner",
            "learn",
            "course"
        ]
    }

def get_search_queries() -> List[str]:
    """Get all search queries from the configuration."""
    config = load_search_queries()
    return config.get("search_queries", [])

# Backward compatibility aliases
def get_primary_search_queries() -> List[str]:
    """Deprecated: Use get_search_queries() instead."""
    return get_search_queries()

def get_additional_search_queries() -> List[str]:
    """Deprecated: Use get_search_queries() instead."""
    return get_search_queries()

def get_all_search_queries() -> List[str]:
    """Deprecated: Use get_search_queries() instead."""
    return get_search_queries()
