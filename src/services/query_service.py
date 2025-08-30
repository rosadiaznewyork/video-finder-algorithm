"""
Centralized service for managing YouTube search queries.
Integrates with Ollama AI to generate dynamic search queries.
"""

from typing import List, Optional

from src.ollama.keyword_generator import generate_default_coding_queries, generate_keywords_from_topic
from src.config.app_config import DEFAULT_CODING_QUERIES


class QueryService:
    """
    Centralized service for managing YouTube search queries.
    Provides AI-generated queries with fallback to static queries.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize the QueryService.
        
        Args:
            db_path: Path to the database for personalized keywords
        """
        self.db_path = db_path
    
    def get_default_queries(self, use_ai: bool = True, num_queries: int = 15) -> List[str]:
        """
        Get default coding search queries.
        
        Args:
            use_ai: Whether to use AI-generated queries (default: True)
            num_queries: Number of queries to generate/return
            
        Returns:
            List of search queries
        """
        if use_ai:
            ai_queries = generate_default_coding_queries(num_queries, self.db_path)
            if ai_queries:
                return ai_queries
            else:
                print("AI query generation failed, falling back to default queries")
        
        # Fallback to static queries
        return DEFAULT_CODING_QUERIES[:num_queries]
    
    def get_additional_queries(self, use_ai: bool = True, num_queries: int = 10) -> List[str]:
        """
        Get additional search queries for expanding video search.
        
        Args:
            use_ai: Whether to use AI-generated queries (default: True)
            num_queries: Number of queries to generate
            
        Returns:
            List of search queries
        """
        if use_ai:
            ai_queries = generate_default_coding_queries(num_queries, self.db_path)
            if ai_queries:
                return ai_queries
        
        # Fallback to hardcoded additional queries
        fallback_queries = [
            "python tutorial",
            "web development course", 
            "coding interview prep",
            "javascript frameworks",
            "database tutorial",
            "react tutorial",
            "node.js tutorial", 
            "data structures algorithms",
            "system design",
            "software engineering"
        ]
        
        return fallback_queries[:num_queries]
    
    def get_topic_queries(self, topic: str, num_queries: int = 8) -> Optional[List[str]]:
        """
        Generate search queries for a specific topic using AI.
        
        Args:
            topic: The topic to generate queries for
            num_queries: Number of queries to generate
            
        Returns:
            List of search queries or None if generation fails
        """
        return generate_keywords_from_topic(topic, num_queries)