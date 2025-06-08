from django.core.cache import cache
from googleapiclient.discovery import build
from django.conf import settings
import re
from datetime import datetime
import hashlib
import logging

try:
    from ai_search import optimize_query
except ImportError:
    optimize_query = None

logger = logging.getLogger(__name__)

YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY
CACHE_TIMEOUT = 3600 * 6

def make_safe_cache_key(prefix, *args):
    raw_key = "_".join(str(arg) for arg in args)
    hashed_key = hashlib.md5(raw_key.encode()).hexdigest()
    return f"{prefix}_{hashed_key}"

def parse_youtube_duration(duration):
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds

def search_youtube_videos(query, max_results=10, user_details=None):
    goal = user_details.goal if user_details else 'default'
    cache_key = make_safe_cache_key("youtube_search", query, max_results, goal)
    cached = cache.get(cache_key)
    if cached:
        return cached

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    base_query = f"{query} workout"
    if optimize_query:
        try:
            base_query = optimize_query(query, user_details=user_details)
        except Exception as e:
            logger.warning(f"AI query optimization failed: {e}")

    if not optimize_query and user_details:
        if user_details.goal == 'lose-weight':
            base_query += " fat burning"
        elif user_details.goal == 'gain-muscle':
            base_query += " muscle building"
        base_query += f" {user_details.training_level}"

    try:
        search_response = youtube.search().list(
            q=base_query,
            part="snippet",
            type="video",
            maxResults=max_results * 3,
            videoDuration="medium",
            relevanceLanguage="en",
            order="viewCount",
            safeSearch="strict"
        ).execute()

        video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
        if not video_ids:
            return []

        videos_response = youtube.videos().list(
            id=",".join(video_ids),
            part="contentDetails,statistics,status",
            maxResults=max_results * 3
        ).execute()

        filtered = []
        for item in videos_response.get("items", []):
            if item["status"]["privacyStatus"] != "public" or not item["status"].get("embeddable", False):
                continue
            duration = parse_youtube_duration(item["contentDetails"]["duration"])
            if not (420 <= duration <= 1800):
                continue

            search_item = next((si for si in search_response["items"] if si["id"]["videoId"] == item["id"]), None)
            if not search_item:
                continue

            filtered.append({
                "title": search_item["snippet"]["title"],
                "description": search_item["snippet"].get("description", ""),
                "video_url": f"https://www.youtube.com/watch?v={item['id']}",
                "embed_url": item["id"],
                "duration": duration,
                "views": int(item["statistics"].get("viewCount", 0)),
                "channel": search_item["snippet"]["channelTitle"],
                "published_at": search_item["snippet"]["publishedAt"],
                "video_id": item["id"],
                "score": 0
            })

        filtered = apply_advanced_filters(filtered, user_details)
        final = filtered[:max_results]
        cache.set(cache_key, final, CACHE_TIMEOUT)
        return final

    except Exception as e:
        logger.error(f"YouTube API error: {e}")
        return []

def apply_advanced_filters(videos, user_details):
    TRUSTED_CHANNELS = [
        "Chloe Ting", "Pamela Reif", "Heather Robertson",
        "Yoga With Adriene", "Fitness Blender", "Blogilates",
        "MadFit", "POPSUGAR Fitness", "The Body Coach TV",
        "Athlean-X", "Buff Dudes",
        "Scott Herman Fitness", "FitnessFAQs", "Natacha Océane"
    ]
    KEYWORD_BLACKLIST = [
        "compilation", "fail", "funny", "challenge",
        "extreme", "competition", "prank", "try not to laugh",
        "dumbbells", "resistance bands", "kettlebells", "dumbbell", "gym",
    ]

    result = []
    for video in videos:
        score = 0

        if any(c.lower() in video["channel"].lower() for c in TRUSTED_CHANNELS):
            score += 50

        score += min(30, video["views"] / 100_000)

        try:
            published = datetime.strptime(video["published_at"], "%Y-%m-%dT%H:%M:%SZ")
            age_days = (datetime.now() - published).days
            score += max(0, 20 - (age_days / 30))
        except Exception:
            score += 5

        combined_text = (video["title"] + " " + video["description"]).lower()
        if any(bad in combined_text for bad in KEYWORD_BLACKLIST):
            continue

        if any(term in video["title"].lower() for term in ["workout", "exercise", "training"]):
            score += 20

        if user_details:
            goal = user_details.goal
            title = video["title"].lower()
            if goal == 'lose-weight' and ("fat burn" in title or "weight loss" in title):
                score += 15
            elif goal == 'gain-muscle' and ("muscle build" in title or "strength" in title):
                score += 15
            elif goal == 'maintain' and ("full body" in title or "balanced" in title):
                score += 10
            if user_details.training_level.lower() in title:
                score += 10

        video["score"] = score
        result.append(video)

    return sorted(result, key=lambda v: v["score"], reverse=True)