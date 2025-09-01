from sklearn.ensemble import RandomForestClassifier
import pandas as pd

def create_recommendation_model():
    return RandomForestClassifier(n_estimators=100, random_state=42)

def train_model_on_user_preferences(model, training_data: pd.DataFrame) -> bool:
    if len(training_data) < 10:
        print("Need at least 10 rated videos to train model")
        return False

    feature_columns = [
        'title_length', 'description_length', 'view_like_ratio', 'engagement_score',
        'title_sentiment', 'has_tutorial_keywords', 'has_time_constraint',
        'has_beginner_keywords', 'has_tech_keywords', 'has_project_keywords'
    ]

    X = training_data[feature_columns]
    y = training_data['liked']

    model.fit(X, y)
    print(f"Model trained on {len(training_data)} rated videos")
    return True