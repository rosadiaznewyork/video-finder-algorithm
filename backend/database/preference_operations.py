import sqlite3
import pandas as pd

def save_video_rating_to_database(video_id: str, liked: bool, notes: str, db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO preferences (video_id, liked, notes) VALUES (?, ?, ?)
    ''', (video_id, liked, notes))

    conn.commit()
    conn.close()

def get_training_data_from_database(db_path: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    query = '''
        SELECT vf.*, p.liked
        FROM video_features vf
        JOIN preferences p ON vf.video_id = p.video_id
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_unrated_videos_with_features_from_database(db_path: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    query = '''
        SELECT v.*, vf.*
        FROM videos v
        JOIN video_features vf ON v.id = vf.video_id
        LEFT JOIN preferences p ON v.id = p.video_id
        WHERE p.video_id IS NULL
        ORDER BY v.view_count DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_rated_count_from_database(db_path: str) -> int:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM preferences")
    count = cursor.fetchone()[0]
    conn.close()
    return count