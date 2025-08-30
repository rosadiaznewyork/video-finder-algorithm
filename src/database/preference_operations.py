import sqlite3
import pandas as pd

from src.database.connection import get_database_connection

def save_video_rating_to_database(video_id: str, liked: bool, notes: str, db_path: str):
    """Save video rating to database using context manager for safe connection handling."""
    with get_database_connection(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO preferences (video_id, liked, notes) VALUES (?, ?, ?)
        ''', (video_id, liked, notes))

def get_training_data_from_database(db_path: str) -> pd.DataFrame:
    """Get training data from database using context manager for safe connection handling."""
    with get_database_connection(db_path) as conn:
        query = '''
            SELECT vf.*, p.liked
            FROM video_features vf
            JOIN preferences p ON vf.video_id = p.video_id
        '''
        df = pd.read_sql_query(query, conn)
        return df

def get_unrated_videos_with_features_from_database(db_path: str) -> pd.DataFrame:
    """Get unrated videos with features from database using context manager for safe connection handling."""
    with get_database_connection(db_path) as conn:
        query = '''
            SELECT v.*, vf.*
            FROM videos v
            JOIN video_features vf ON v.id = vf.video_id
            LEFT JOIN preferences p ON v.id = p.video_id
            WHERE p.video_id IS NULL
            ORDER BY v.view_count DESC
        '''
        df = pd.read_sql_query(query, conn)
        return df

def get_rated_count_from_database(db_path: str) -> int:
    """Get count of rated videos from database using context manager for safe connection handling."""
    with get_database_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM preferences")
        count = cursor.fetchone()[0]
        return count


def remove_video_preference(video_id: str, db_path: str) -> bool:
    """
    Remove a video preference (rating) from the database.
    
    Args:
        video_id: The video ID to remove preference for
        db_path: Database path
        
    Returns:
        True if preference was removed, False if not found
    """
    with get_database_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Check if preference exists
        cursor.execute("SELECT video_id FROM preferences WHERE video_id = ?", (video_id,))
        if not cursor.fetchone():
            return False
        
        # Remove the preference
        cursor.execute("DELETE FROM preferences WHERE video_id = ?", (video_id,))
        return cursor.rowcount > 0


def get_liked_video_tags(db_path: str) -> list[str]:
    """
    Extract all tags from liked videos in the database.
    
    Args:
        db_path: Database path
        
    Returns:
        Flattened, deduplicated list of tags from liked videos
    """
    import json
    
    with get_database_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Get tags from all liked videos
        cursor.execute('''
            SELECT v.tags
            FROM videos v
            JOIN preferences p ON v.id = p.video_id
            WHERE p.liked = 1 AND v.tags IS NOT NULL AND v.tags != ""
        ''')
        
        all_tags = []
        for row in cursor.fetchall():
            tags_json = row[0]
            if tags_json:
                try:
                    tags = json.loads(tags_json)
                    if isinstance(tags, list):
                        # Clean and normalize tags
                        for tag in tags:
                            if isinstance(tag, str) and tag.strip():
                                clean_tag = tag.strip().lower()
                                if clean_tag not in all_tags:
                                    all_tags.append(clean_tag)
                except (json.JSONDecodeError, TypeError):
                    # Skip malformed JSON
                    continue
        
        return all_tags