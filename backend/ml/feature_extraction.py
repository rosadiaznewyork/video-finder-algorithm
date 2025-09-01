from typing import Dict, Tuple

def calculate_basic_video_metrics(video: Dict) -> Tuple:
    title_length = len(video['title'])
    description_length = len(video['description'])
    view_like_ratio = video['like_count'] / max(video['view_count'], 1)
    engagement_score = (video['like_count'] + video['comment_count']) / max(video['view_count'], 1)

    return (title_length, description_length, view_like_ratio, engagement_score)

def detect_keyword_features_in_video(title: str, description: str) -> Tuple:
    tutorial_keywords = ['tutorial', 'learn', 'course', 'guide', 'how to', 'explained', 'walkthrough']
    time_keywords = ['24 hours', '1 day', '1 hour', 'minutes', 'seconds', 'crash course', 'quick', 'fast']
    beginner_keywords = ['beginner', 'start', 'basics', 'introduction', 'getting started', 'first time', 'new to']
    tech_keywords = ['ai', 'artificial intelligence', 'machine learning', 'neural network', 'coding', 'programming', 'tech']
    project_keywords = ['challenge', 'build', 'create', 'project', 'diy', 'make', 'workout', 'routine', 'recipe']

    has_tutorial = any(kw in title.lower() or kw in description.lower() for kw in tutorial_keywords)
    has_time_constraint = any(kw in title.lower() for kw in time_keywords)
    has_beginner = any(kw in title.lower() or kw in description.lower() for kw in beginner_keywords)
    has_tech = any(kw in title.lower() or kw in description.lower() for kw in tech_keywords)
    has_project = any(kw in title.lower() for kw in project_keywords)

    return (has_tutorial, has_time_constraint, has_beginner, has_tech, has_project)

def calculate_title_sentiment_score(title: str) -> float:
    positive_words = ['amazing', 'best', 'awesome', 'great', 'perfect', 'love', 'incredible']
    negative_words = ['hard', 'difficult', 'impossible', 'failed', 'broke', 'wrong']

    positive_count = sum(1 for word in positive_words if word in title)
    negative_count = sum(1 for word in negative_words if word in title)
    return positive_count - negative_count

def extract_all_features_from_video(video: Dict) -> Tuple:
    title = video['title'].lower()
    description = video['description'].lower()

    basic_metrics = calculate_basic_video_metrics(video)
    keyword_features = detect_keyword_features_in_video(title, description)
    sentiment_score = calculate_title_sentiment_score(title)

    return basic_metrics + keyword_features + (sentiment_score,)