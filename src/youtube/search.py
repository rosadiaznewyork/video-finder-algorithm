"""
Compatibility module for legacy search functionality.
Provides backward compatibility after refactoring to service-based architecture.
"""

from typing import List
from src.config.app_config import DEFAULT_CODING_QUERIES


def get_coding_search_queries() -> List[str]:
    """
    Get default coding search queries.
    
    Returns:
        List of default search queries for coding videos
    """
    return DEFAULT_CODING_QUERIES