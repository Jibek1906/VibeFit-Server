from django.core.cache import cache
from googleapiclient.discovery import build
from django.conf import settings
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY
CACHE_TIMEOUT = 3600 * 6

def is_video_available(video_id):
    """Check if video is public and embeddable with caching"""
    cache_key = f"video_available_{video_id}"
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    try:
        stats_request = youtube.videos().list(
            part="status",
            id=video_id
        )
        stats_response = stats_request.execute()

        if not stats_response.get("items"):
            result = (False, False)
        else:
            status = stats_response["items"][0]['status']
            result = (
                status.get("privacyStatus") == "public",
                status.get("embeddable", False)
            )
        cache.set(cache_key, result, CACHE_TIMEOUT)
        return result

    except Exception as e:
        logger.error(f"Error checking video availability {video_id}: {e}")
        return (False, False)

def parse_youtube_duration(duration):
    """Parse YouTube duration string into seconds."""
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds

def search_youtube_videos(query, max_results=10, user_details=None):
    """Enhanced YouTube search with better filtering and caching"""
    cache_key = f"youtube_search_{query}_{max_results}_{user_details.goal if user_details else 'default'}"
    cached_videos = cache.get(cache_key)
    if cached_videos:
        return cached_videos

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    try:
        base_query = f"{query} workout"
        if user_details:
            if user_details.goal == 'lose-weight':
                base_query += " fat burning"
            elif user_details.goal == 'gain-muscle':
                base_query += " muscle building"
            base_query += f" {user_details.training_level}"

        search_request = youtube.search().list(
            q=base_query,
            part="snippet",
            type="video",
            maxResults=max_results * 3,
            videoDuration="medium",
            relevanceLanguage="en",
            order="viewCount",
            safeSearch="strict"
        )
        search_response = search_request.execute()

        video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
        if not video_ids:
            return []

        videos_request = youtube.videos().list(
            id=",".join(video_ids),
            part="contentDetails,statistics,status",
            maxResults=max_results * 3
        )
        videos_response = videos_request.execute()

        filtered_videos = []
        for item in videos_response.get("items", []):
            if item["status"]["privacyStatus"] != "public" or not item["status"].get("embeddable", False):
                continue

            duration = item["contentDetails"]["duration"]
            duration_sec = parse_youtube_duration(duration)
            if not (420 <= duration_sec <= 1800):
                continue

            search_item = next(
                (si for si in search_response["items"] if si["id"]["videoId"] == item["id"]),
                None
            )
            if not search_item:
                continue

            filtered_videos.append({
                "title": search_item["snippet"]["title"],
                "video_url": f"https://www.youtube.com/watch?v={item['id']}",
                "embed_url": item["id"],
                "duration": duration_sec,
                "views": int(item["statistics"].get("viewCount", 0)),
                "channel": search_item["snippet"]["channelTitle"],
                "published_at": search_item["snippet"]["publishedAt"],
                "video_id": item["id"],
                "score": 0
            })

        filtered_videos = apply_advanced_filters(filtered_videos, user_details)

        final_videos = filtered_videos[:max_results]
        cache.set(cache_key, final_videos, CACHE_TIMEOUT)
        return final_videos

    except Exception as e:
        logger.error(f"YouTube API error: {e}")
        return []

def apply_advanced_filters(videos, user_details):
    """Apply additional filters based on user details and video quality"""
    TRUSTED_CHANNELS = [
        "Chloe Ting", "Pamela Reif", "Heather Robertson",
        "Yoga With Adriene", "Fitness Blender", "Blogilates",
        "MadFit", "POPSUGAR Fitness", "The Body Coach TV"
    ]

    KEYWORD_BLACKLIST = [
        "compilation", "fail", "funny", "challenge",
        "extreme", "competition", "prank", "try not to laugh" 'Dumbbells', 'Resistance Bands', 'Kettlebells',
    ]

    scored_videos = []
    for video in videos:
        score = 0

        if any(channel.lower() in video["channel"].lower() for channel in TRUSTED_CHANNELS):
            score += 50

        score += min(30, video["views"] / 100000)

        try:
            published_date = datetime.strptime(video["published_at"], "%Y-%m-%dT%H:%M:%SZ")
            days_old = (datetime.now() - published_date).days
            score += max(0, 20 - (days_old / 30))
        except:
            days_old = 365
            score += 5

        title = video["title"].lower()
        if any(bad in title for bad in KEYWORD_BLACKLIST):
            continue

        if "workout" in title or "exercise" in title or "training" in title:
            score += 20

        if user_details:
            if user_details.goal == 'lose-weight' and ("fat burn" in title or "weight loss" in title):
                score += 15
            elif user_details.goal == 'gain-muscle' and ("muscle build" in title or "strength" in title):
                score += 15
            elif user_details.goal == 'maintain' and ("full body" in title or "balanced" in title):
                score += 10

        if user_details and user_details.training_level.lower() in title:
            score += 10

        video["score"] = score
        scored_videos.append(video)

    return sorted(scored_videos, key=lambda x: x["score"], reverse=True)