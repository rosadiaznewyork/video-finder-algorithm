import sqlite3
from datetime import datetime
from typing import List, Dict, Tuple

def save_videos_to_database(videos: List[Dict], db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for video in videos:
        cursor.execute('''
            INSERT OR REPLACE INTO videos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            video['id'], video['title'], video['description'],
            video['view_count'], video['like_count'], video['comment_count'],
            video['duration'], video['published_at'], video['channel_name'],
            video['thumbnail_url'], video['tags'], video['category_id'],
            datetime.now().isoformat()
        ))

    conn.commit()
    conn.close()

def save_video_features_to_database(video_id: str, features: Tuple, db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO video_features VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (video_id,) + features)

    conn.commit()
    conn.close()

def get_unrated_videos_from_database(limit: int, db_path: str) -> List[Dict]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT v.*
        FROM videos v
        LEFT JOIN preferences p ON v.id = p.video_id
        WHERE p.video_id IS NULL
        ORDER BY v.view_count DESC
        LIMIT ?
    ''', (limit,))

    videos = []
    for row in cursor.fetchall():
        videos.append({
            'id': row[0],
            'title': row[1],
            'channel_name': row[8],
            'view_count': row[3],
            'url': f"https://www.youtube.com/watch?v={row[0]}"
        })

    conn.close()
    return videos