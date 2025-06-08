import random
from workouts.youtube_api import search_youtube_videos
from users.models import UserDetails


def get_burn_videos(calories_needed, user_details, max_videos=3):
    """
    Подбирает YouTube видео для сжигания калорий по профилю пользователя.
    """
    queries = generate_burn_queries(user_details, calories_needed)

    all_videos = []
    seen = set()
 
    for query in queries:
        results = search_youtube_videos(query, max_results=5, user_details=user_details)
        for video in results:
            if video['video_id'] not in seen:
                seen.add(video['video_id'])
                all_videos.append({
                    'title': video['title'],
                    'video_id': video['video_id'],
                    'calories': estimate_video_calories(video, user_details),
                    'embed_url': f"https://www.youtube.com/embed/{video['video_id']}",
                })

    # Убираем дубликаты и сортируем
    random.shuffle(all_videos)
    sorted_videos = sorted(all_videos, key=lambda x: -x['calories'])

    selected = []
    total = 0
    for v in sorted_videos:
        if total >= calories_needed or len(selected) >= max_videos:
            break
        selected.append(v)
        total += v['calories']

    return selected


def generate_burn_queries(user, calories_needed):
    """
    Создаёт поисковые запросы под цель – сжечь лишние калории.
    """
    base = f"{user.training_level} fat burning"
    queries = []

    if calories_needed < 200:
        queries = [f"{base} quick workout", f"{base} 10 minutes"]
    elif calories_needed < 400:
        queries = [f"{base} 20 minutes", f"{base} hiit", f"{base} full body"]
    else:
        queries = [f"{base} 30 minutes", f"{base} intense hiit", f"{base} no equipment"]

    return queries


def estimate_video_calories(video, user):
    """
    Примерная оценка калорийности видео (можно заменить на ML-модель).
    """
    title = video['title'].lower()
    duration = video.get('duration', 15)  # можно добавить парсинг длительности
    intensity = 8 if 'hiit' in title or 'intense' in title else 5

    weight = float(user.weight)
    # MET формула: калории в минуту = (MET * вес(кг) * 3.5) / 200
    met = intensity
    per_minute = (met * weight * 3.5) / 200
    estimated = int(duration * per_minute)

    return min(estimated, 500)
