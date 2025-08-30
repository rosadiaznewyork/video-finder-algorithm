from typing import List, Dict
import pandas as pd

def predict_video_preferences_with_model(model, video_features: pd.DataFrame, top_n: int = 10) -> List[Dict]:
    if video_features.empty:
        return []

    feature_columns = [
        'title_length', 'description_length', 'view_like_ratio', 'engagement_score',
        'title_sentiment', 'has_tutorial_keywords', 'has_time_constraint',
        'has_beginner_keywords', 'has_ai_keywords', 'has_challenge_keywords'
    ]

    X = video_features[feature_columns]
    probabilities = model.predict_proba(X)[:, 1]
    
    video_features_copy = video_features.copy()
    video_features_copy['like_probability'] = probabilities

    top_videos = video_features_copy.nlargest(top_n, 'like_probability')

    recommendations = []
    for _, row in top_videos.iterrows():
        recommendations.append({
            'id': row['id'],
            'title': row['title'],
            'channel_name': row['channel_name'],
            'view_count': row['view_count'],
            'url': f"https://www.youtube.com/watch?v={row['id']}",
            'like_probability': row['like_probability']
        })

    return recommendations