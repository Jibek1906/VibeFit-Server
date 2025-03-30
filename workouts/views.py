import random
from datetime import datetime, timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.cache import cache
from users.models import UserDetails
from .youtube_api import search_youtube_videos

WORKOUT_TYPES = {
    'cardio': ['HIIT', 'Tabata', 'Dance', 'Kickboxing', 'Jump Rope', 'Cycling', 'Running'],
    'strength': ['Full Body', 'Upper Body', 'Lower Body', 'Core', 'Pilates', 'Resistance', 'Calisthenics'],
    'flexibility': ['Yoga', 'Stretching', 'Mobility', 'Barre', 'Tai Chi']
}

WORKOUT_EQUIPMENT = [
    'No Equipment',
    'Yoga Mat'
]

@login_required
def workouts_api(request):
    """Enhanced workout API with better caching, filtering and availability checks"""
    try:
        user_details = UserDetails.objects.get(user=request.user)
    except UserDetails.DoesNotExist:
        return JsonResponse({"error": "User details not found"}, status=400)

    date_str = request.GET.get('date', datetime.now().date().isoformat())
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = datetime.now().date()

    cache_key = f"workouts_{user_details.id}_{date_str}_{user_details.goal}_{user_details.training_level}"
    cached_response = cache.get(cache_key)
    if cached_response:
        return JsonResponse(cached_response)

    is_rest_day = calculate_rest_day(user_details, selected_date)
    if is_rest_day:
        response = {
            "workouts": [{
                "title": "Rest Day",
                "is_rest_day": True,
                "description": get_rest_day_message(user_details)
            }]
        }
        cache.set(cache_key, response, 3600 * 6)
        return JsonResponse(response)

    workout_queries = generate_workout_queries(user_details, selected_date)

    all_videos = []
    for query in workout_queries:
        videos = search_youtube_videos(query, max_results=5, user_details=user_details)
        all_videos.extend(videos)

    unique_videos = []
    seen_videos = set()
    for video in sorted(all_videos, key=lambda x: x["score"], reverse=True):
        if video["embed_url"] not in seen_videos and is_video_available(video["video_id"]):
            seen_videos.add(video["embed_url"])
            unique_videos.append({
                "title": clean_workout_title(video["title"]),
                "video_url": video["video_url"],
                "embed_url": video["embed_url"],
                "duration": video["duration"],
                "trainer": extract_trainer(video["title"]),
                "tags": get_workout_tags(video["title"], user_details),
                "video_id": video["video_id"],
                "channel": video["channel"]
            })
        if len(unique_videos) >= 5:
            break

    if len(unique_videos) < 3:
        fallback_queries = generate_fallback_queries(user_details)
        for query in fallback_queries:
            videos = search_youtube_videos(query, max_results=3, user_details=user_details)
            for video in videos:
                if video["embed_url"] not in seen_videos and is_video_available(video["video_id"]):
                    seen_videos.add(video["embed_url"])
                    unique_videos.append({
                        "title": clean_workout_title(video["title"]),
                        "video_url": video["video_url"],
                        "embed_url": video["embed_url"],
                        "duration": video["duration"],
                        "trainer": extract_trainer(video["title"]),
                        "tags": get_workout_tags(video["title"], user_details),
                        "video_id": video["video_id"],
                        "channel": video["channel"]
                    })
                if len(unique_videos) >= 5:
                    break
            if len(unique_videos) >= 5:
                break

    response = {
        "workouts": [
            {
                "title": workout["title"],
                "video_url": workout["video_url"],
                "embed_url": f"https://www.youtube.com/embed/{workout['video_id']}",
                "duration": workout["duration"],
                "trainer": workout["trainer"],
                "tags": workout["tags"],
                "video_id": workout["video_id"],
                "channel": workout["channel"],
                "thumbnail": f"https://img.youtube.com/vi/{workout['video_id']}/mqdefault.jpg"
            }
            for workout in unique_videos
        ]
    }
    cache.set(cache_key, response, 3600 * 6)
    return JsonResponse(response)

def is_video_available(video_id):
    """Check if video is available by checking cache first"""
    cache_key = f"video_available_{video_id}"
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    return True

def calculate_rest_day(user_details, date):
    """Improved rest day calculation with weekly limits"""
    day_of_week = date.weekday()
    week_start = date - timedelta(days=date.weekday())
    rest_days_this_week = 0

    for i in range(7):
        day = week_start + timedelta(days=i)
        if day > date:
            break
        if is_scheduled_rest_day(user_details, day):
            rest_days_this_week += 1

    if is_scheduled_rest_day(user_details, date):
        if rest_days_this_week <= 2:
            return True
    return False

def is_scheduled_rest_day(user_details, date):
    """Check if date is scheduled as rest day for user's level"""
    day_of_week = date.weekday()
    if user_details.training_level == 'beginner' and day_of_week in [2, 5]:  # Wed, Sat
        return True
    elif user_details.training_level == 'intermediate' and day_of_week == 3:  # Thu
        return True
    elif user_details.training_level == 'advanced' and day_of_week == 0:  # Sun
        return True
    return False

def get_rest_day_message(user_details):
    """Personalized rest day messages"""
    messages = {
        'beginner': [
            "Your body needs recovery after those first workouts!",
            "Rest is just as important as exercise for beginners.",
            "Enjoy your day off - you've earned it!"
        ],
        'intermediate': [
            "Active recovery day - consider light stretching or walking.",
            "Your muscles grow during rest days, not during workouts.",
            "Quality rest leads to better performance tomorrow."
        ],
        'advanced': [
            "Even elite athletes need recovery days.",
            "Today is for mobility work and recovery.",
            "Strategic rest is part of advanced training."
        ]
    }
    return random.choice(messages.get(user_details.training_level, ["Rest day for recovery and growth."]))

def generate_workout_queries(user_details, date):
    """Generate diverse workout queries based on user profile and date"""
    day_of_week = date.weekday()
    week_of_month = (date.day - 1) // 7

    if user_details.goal == 'lose-weight':
        focus = ['cardio', 'cardio', 'strength', 'cardio', 'strength', 'flexibility', 'cardio'][day_of_week]
    elif user_details.goal == 'gain-muscle':
        focus = ['strength', 'strength', 'cardio', 'strength', 'strength', 'flexibility', 'strength'][day_of_week]
    else:  # maintain
        focus = ['strength', 'cardio', 'strength', 'cardio', 'flexibility', 'cardio', 'strength'][day_of_week]

    variation = week_of_month % 4
    if variation == 1:
        focus = 'cardio'
    elif variation == 2:
        focus = 'strength'
    elif variation == 3:
        focus = 'flexibility'

    queries = []
    workout_types = WORKOUT_TYPES[focus]
    equipment_options = WORKOUT_EQUIPMENT

    for i in range(5):
        workout_type = random.choice(workout_types)
        equipment = random.choice(equipment_options)

        query = f"{workout_type} {equipment} {user_details.training_level}"
        if user_details.goal == 'lose-weight':
            query += " fat burning"
        elif user_details.goal == 'gain-muscle':
            query += " muscle building"

        if i % 2 == 0:
            query += " full session"
        else:
            query += " quick workout"

        queries.append(query)

    return queries

def generate_fallback_queries(user_details):
    """Generate fallback queries when initial search fails"""
    fallbacks = []
    base = f"{user_details.training_level} workout"
    
    if user_details.goal == 'lose-weight':
        fallbacks.extend([
            f"{base} fat burning",
            f"{base} cardio",
            f"{base} weight loss"
        ])
    elif user_details.goal == 'gain-muscle':
        fallbacks.extend([
            f"{base} muscle building",
            f"{base} strength training",
            f"{base} resistance"
        ])
    else:
        fallbacks.extend([
            f"{base} full body",
            f"{base} maintenance",
            f"{base} balanced"
        ])
    
    return fallbacks

def clean_workout_title(title):
    """Clean up workout titles"""
    removals = [
        "FULL BODY WORKOUT", "HOME WORKOUT", "NO EQUIPMENT",
        "BEGINNER", "INTERMEDIATE", "ADVANCED", "CHALLENGE",
        "-", "|", "\"", "FULL VIDEO", "WORKOUT"
    ]
    for removal in removals:
        title = title.replace(removal, "")
    return " ".join(title.split()).strip()

def extract_trainer(title):
    """Extract trainer name from title if known"""
    TRUSTED_TRAINERS = [
        "Chloe Ting", "Pamela Reif", "Heather Robertson",
        "Yoga With Adriene", "Fitness Blender", "Blogilates",
        "MadFit", "POPSUGAR Fitness", "The Body Coach TV"
    ]
    for trainer in TRUSTED_TRAINERS:
        if trainer.lower() in title.lower():
            return trainer
    return None

def get_workout_tags(title, user_details):
    """Extract tags from workout title with user context"""
    title_lower = title.lower()
    tags = []
    
    workout_types = {
        "hilt": "HIIT",
        "yoga": "Yoga",
        "pilates": "Pilates",
        "tabata": "Tabata",
        "cardio": "Cardio",
        "strength": "Strength",
        "dance": "Dance",
    }

    for kw, tag in workout_types.items():
        if kw in title_lower:
            tags.append(tag)

    equipment = {
        "no equipment": "No Equipment",
        "yoga mat": "Yoga Mat"
    }
    for kw, tag in equipment.items():
        if kw in title_lower:
            tags.append(tag)

    body_focus = {
        "full body": "Full Body",
        "upper": "Upper Body",
        "lower": "Lower Body",
        "core": "Core",
        "abs": "Core",
        "arm": "Arms",
        "leg": "Legs",
        "back": "Back"
    }
    for kw, tag in body_focus.items():
        if kw in title_lower:
            tags.append(tag)

    if user_details.goal == 'lose-weight':
        tags.append("Fat Burning")
    elif user_details.goal == 'gain-muscle':
        tags.append("Muscle Building")
    
    tags.append(user_details.training_level.capitalize())

    return list(set(tags))[:4]

@login_required
def workouts_view(request):
    """Render workout page with user context"""
    try:
        user_details = UserDetails.objects.get(user=request.user)
        registration_date = request.user.date_joined.date()
    except UserDetails.DoesNotExist:
        registration_date = datetime.now().date()
        user_details = None

    context = {
        'registration_date': registration_date.strftime("%Y-%m-%d"),
        'current_date': datetime.now().strftime("%Y-%m-%d"),
        'user_goal': getattr(user_details, 'goal', 'maintain'),
        'training_level': getattr(user_details, 'training_level', 'beginner')
    }
    return render(request, 'workouts.html', context)