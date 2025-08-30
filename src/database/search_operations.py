import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from src.database.connection import get_database_connection


def create_search_session(topic: str, db_path: str) -> str:
    """
    Create a new search session.
    
    Args:
        topic: The search topic
        db_path: Database path
        
    Returns:
        The session ID
    """
    session_id = str(uuid.uuid4())
    
    with get_database_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO search_sessions (id, topic) VALUES (?, ?)
        ''', (session_id, topic))
    
    return session_id


def update_search_session_video_count(session_id: str, video_count: int, db_path: str):
    """
    Update the video count for a search session.
    
    Args:
        session_id: The session ID
        video_count: Number of videos found
        db_path: Database path
    """
    with get_database_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE search_sessions 
            SET video_count = ? 
            WHERE id = ?
        ''', (video_count, session_id))


def get_search_session(session_id: str, db_path: str) -> Optional[Dict]:
    """
    Get search session details.
    
    Args:
        session_id: The session ID
        db_path: Database path
        
    Returns:
        Search session dictionary or None if not found
    """
    with get_database_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM search_sessions WHERE id = ?
        ''', (session_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
    return None


def get_recent_search_sessions(limit: int = 10, db_path: str = None) -> List[Dict]:
    """
    Get recent search sessions.
    
    Args:
        limit: Maximum number of sessions to return
        db_path: Database path
        
    Returns:
        List of search session dictionaries
    """
    with get_database_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM search_sessions 
            WHERE status = 'active'
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]


def get_videos_by_search_session(session_id: str, db_path: str) -> List[Dict]:
    """
    Get all videos from a specific search session.
    
    Args:
        session_id: The session ID
        db_path: Database path
        
    Returns:
        List of video dictionaries
    """
    with get_database_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.*, vf.*
            FROM videos v
            JOIN video_features vf ON v.id = vf.video_id
            WHERE v.search_session_id = ?
            ORDER BY v.view_count DESC
        ''', (session_id,))
        
        videos = []
        for row in cursor.fetchall():
            video = dict(row)
            video['url'] = f"https://www.youtube.com/watch?v={video['id']}"
            videos.append(video)
        
        return videos


def cleanup_old_search_sessions(days_old: int = 7, db_path: str = None):
    """
    Clean up old search sessions and their associated videos.
    
    Args:
        days_old: Age threshold in days
        db_path: Database path
        
    Returns:
        Number of sessions cleaned up
    """
    cutoff_date = datetime.now() - timedelta(days=days_old)
    
    with get_database_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Find old search sessions
        cursor.execute('''
            SELECT id FROM search_sessions 
            WHERE created_at < ? AND status = 'active'
        ''', (cutoff_date.isoformat(),))
        
        old_sessions = [row[0] for row in cursor.fetchall()]
        
        if not old_sessions:
            return 0
        
        # Mark sessions as archived instead of deleting (preserve data integrity)
        cursor.execute('''
            UPDATE search_sessions 
            SET status = 'archived' 
            WHERE created_at < ? AND status = 'active'
        ''', (cutoff_date.isoformat(),))
        
        # Optionally remove video associations (but keep videos for other purposes)
        # Uncomment if you want to clear the search session links:
        # placeholders = ','.join('?' * len(old_sessions))
        # cursor.execute(f'''
        #     UPDATE videos 
        #     SET search_session_id = NULL, search_topic = NULL
        #     WHERE search_session_id IN ({placeholders})
        # ''', old_sessions)
        
        return len(old_sessions)


def get_search_sessions_stats(db_path: str) -> Dict:
    """
    Get statistics about search sessions.
    
    Args:
        db_path: Database path
        
    Returns:
        Dictionary with search session statistics
    """
    with get_database_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Total sessions
        cursor.execute("SELECT COUNT(*) FROM search_sessions")
        total_sessions = cursor.fetchone()[0]
        
        # Active sessions
        cursor.execute("SELECT COUNT(*) FROM search_sessions WHERE status = 'active'")
        active_sessions = cursor.fetchone()[0]
        
        # Total videos from searches
        cursor.execute("SELECT COUNT(*) FROM videos WHERE search_session_id IS NOT NULL")
        search_videos = cursor.fetchone()[0]
        
        # Recent sessions (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('''
            SELECT COUNT(*) FROM search_sessions 
            WHERE created_at > ? AND status = 'active'
        ''', (week_ago,))
        recent_sessions = cursor.fetchone()[0]
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'archived_sessions': total_sessions - active_sessions,
            'search_videos': search_videos,
            'recent_sessions': recent_sessions
        }


def delete_search_session(session_id: str, db_path: str, remove_videos: bool = False) -> bool:
    """
    Delete a search session and optionally its videos.
    
    Args:
        session_id: The session ID to delete
        db_path: Database path
        remove_videos: Whether to also remove associated videos
        
    Returns:
        True if session was deleted, False if not found
    """
    with get_database_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Check if session exists
        cursor.execute("SELECT id FROM search_sessions WHERE id = ?", (session_id,))
        if not cursor.fetchone():
            return False
        
        if remove_videos:
            # Get video IDs for this session
            cursor.execute('''
                SELECT id FROM videos WHERE search_session_id = ?
            ''', (session_id,))
            video_ids = [row[0] for row in cursor.fetchall()]
            
            if video_ids:
                # Remove video features
                placeholders = ','.join('?' * len(video_ids))
                cursor.execute(f'''
                    DELETE FROM video_features WHERE video_id IN ({placeholders})
                ''', video_ids)
                
                # Remove preferences for these videos
                cursor.execute(f'''
                    DELETE FROM preferences WHERE video_id IN ({placeholders})
                ''', video_ids)
                
                # Remove videos
                cursor.execute(f'''
                    DELETE FROM videos WHERE id IN ({placeholders})
                ''', video_ids)
        else:
            # Just clear the session association
            cursor.execute('''
                UPDATE videos 
                SET search_session_id = NULL, search_topic = NULL
                WHERE search_session_id = ?
            ''', (session_id,))
        
        # Delete the session
        cursor.execute("DELETE FROM search_sessions WHERE id = ?", (session_id,))
        
        return True