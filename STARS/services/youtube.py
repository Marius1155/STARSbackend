import httpx
import re
from typing import Dict, Any, List
from decouple import config

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"
YOUTUBE_API_KEY = config("YOUTUBE_API_KEY")


class YoutubeService:
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def search_videos(self, term: str, limit: int = 20) -> List[Dict[str, Any]]:
        url = f"{YOUTUBE_API_URL}/search"
        params = {
            "part": "snippet",
            "q": term,
            "type": "video",
            "maxResults": limit,
            "key": YOUTUBE_API_KEY
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId")

            if video_id:
                results.append({
                    "id": video_id,
                    "title": snippet.get("title"),
                    "description": snippet.get("description"),
                    "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                    "channel_title": snippet.get("channelTitle"),
                    "published_at": snippet.get("publishedAt"),
                })
        return results

    async def get_video_details(self, video_id: str) -> Dict[str, Any]:
        url = f"{YOUTUBE_API_URL}/videos"
        params = {
            "part": "snippet,contentDetails,statistics",
            "id": video_id,
            "key": YOUTUBE_API_KEY
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])

        if not items:
            return {}

        item = items[0]
        snippet = item.get("snippet", {})
        content_details = item.get("contentDetails", {})
        statistics = item.get("statistics", {})

        # Parse duration to milliseconds
        duration_iso = content_details.get("duration", "")
        duration_ms = self._parse_duration_to_ms(duration_iso)

        # Get the best available thumbnail
        thumbnails = snippet.get("thumbnails", {})
        thumbnail_url = thumbnails.get("maxres", {}).get("url") or \
                        thumbnails.get("high", {}).get("url") or \
                        thumbnails.get("medium", {}).get("url")

        return {
            "id": video_id,
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "thumbnail": thumbnail_url,
            "channel_title": snippet.get("channelTitle"),
            "published_at": snippet.get("publishedAt"),
            "length_ms": duration_ms,
            "view_count": int(statistics.get("viewCount", 0)),
            "url": f"https://www.youtube.com/watch?v={video_id}"
        }

    def _parse_duration_to_ms(self, duration_iso: str) -> int:
        """Parses ISO 8601 duration (e.g. PT1H2M10S) to milliseconds."""
        if not duration_iso:
            return 0

        # Regex to extract hours, minutes, and seconds
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_iso)
        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        total_seconds = (hours * 3600) + (minutes * 60) + seconds
        return total_seconds * 1000

    async def close(self):
        await self.client.aclose()