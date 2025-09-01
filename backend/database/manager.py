import sqlite3
from datetime import datetime
from typing import List, Dict

def setup_database_tables(db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            view_count INTEGER,
            like_count INTEGER,
            comment_count INTEGER,
            duration TEXT,
            published_at TEXT,
            channel_name TEXT,
            thumbnail_url TEXT,
            tags TEXT,
            category_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT,
            liked BOOLEAN,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_id) REFERENCES videos (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_features (
            video_id TEXT PRIMARY KEY,
            title_length INTEGER,
            description_length INTEGER,
            view_like_ratio REAL,
            engagement_score REAL,
            title_sentiment REAL,
            has_tutorial_keywords BOOLEAN,
            has_time_constraint BOOLEAN,
            has_beginner_keywords BOOLEAN,
            has_tech_keywords BOOLEAN,
            has_project_keywords BOOLEAN,
            FOREIGN KEY (video_id) REFERENCES videos (id)
        )
    ''')

    conn.commit()
    conn.close()