import httpx
import re
import io
import asyncio
from typing import Dict, Any, List
from decouple import config
from PIL import Image
from asgiref.sync import sync_to_async
from STARS.models import MusicVideo

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"
YOUTUBE_API_KEY = config("YOUTUBE_API_KEY")


class YoutubeService:
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def get_video_by_url(self, url: str) -> Dict[str, Any]:
        """
        Parses the URL to extract the video ID and fetches its details.
        """
        video_id = self._extract_video_id(url)
        if not video_id:
            return None  # Or raise a specific exception

        return await self.get_video_by_id(video_id)

    async def get_video_by_id(self, video_id: str) -> Dict[str, Any]:
        """
        Fetches full details for a single video ID.
        """
        videos_url = f"{YOUTUBE_API_URL}/videos"
        videos_params = {
            "part": "snippet,contentDetails,statistics",
            "id": video_id,
            "key": YOUTUBE_API_KEY
        }

        response = await self.client.get(videos_url, params=videos_params)
        response.raise_for_status()
        data = response.json()

        items = data.get("items", [])
        if not items:
            return None

        item = items[0]
        snippet = item.get("snippet", {})
        content_details = item.get("contentDetails", {})
        statistics = item.get("statistics", {})

        # Duration and Thumbnails
        duration_ms = self._parse_duration_to_ms(content_details.get("duration", ""))
        thumbnails = snippet.get("thumbnails", {})
        thumbnail_url = (thumbnails.get("maxres", {}).get("url") or
                         thumbnails.get("high", {}).get("url") or
                         thumbnails.get("medium", {}).get("url"))

        # Primary Color Extraction
        primary_color = await self._get_primary_color(thumbnail_url)

        return {
            "id": video_id,
            "title": snippet.get("title"),
            "thumbnail": thumbnail_url,
            "channel_title": snippet.get("channelTitle"),
            "published_at": snippet.get("publishedAt"),
            "length_ms": duration_ms,
            "view_count": int(statistics.get("viewCount", 0)),
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "primary_color": primary_color,
        }

    def _extract_video_id(self, url: str) -> str:
        """
        Extracts the video ID from various YouTube URL formats.
        """
        regex = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/|youtube\.com\/shorts\/)([^"&?\/\s]{11})'
        match = re.search(regex, url)
        return match.group(1) if match else None

    async def search_videos(self, term: str, limit: int = 20) -> List[Dict[str, Any]]:
        # 1. Call Search API to get Video IDs
        search_url = f"{YOUTUBE_API_URL}/search"
        search_params = {
            "part": "id",
            "q": term,
            "type": "video",
            "maxResults": limit,
            "key": YOUTUBE_API_KEY
        }

        response = await self.client.get(search_url, params=search_params)
        response.raise_for_status()
        search_data = response.json()

        video_ids = []
        for item in search_data.get("items", []):
            vid = item.get("id", {}).get("videoId")
            if vid:
                video_ids.append(vid)

        if not video_ids:
            return []

        # 2. Filter out videos that are already in the database
        #    Checking 'youtube_id' field against the fetched IDs
        @sync_to_async
        def get_existing_ids(ids):
            # Assumes the field name in the model is 'youtube_id'
            return list(MusicVideo.objects.filter(youtube_id__in=ids).values_list('youtube_id', flat=True))

        existing_ids = set(await get_existing_ids(video_ids))

        # Keep only new IDs
        filtered_ids = [vid for vid in video_ids if vid not in existing_ids]

        if not filtered_ids:
            return []

        # 3. Call Videos API to get full details for the new videos
        videos_url = f"{YOUTUBE_API_URL}/videos"
        videos_params = {
            "part": "snippet,contentDetails,statistics",
            "id": ",".join(filtered_ids),
            "key": YOUTUBE_API_KEY
        }

        vid_response = await self.client.get(videos_url, params=videos_params)
        vid_response.raise_for_status()
        vid_data = vid_response.json()

        results = []
        color_tasks = []

        # 4. Process details and prepare color extraction tasks
        for item in vid_data.get("items", []):
            snippet = item.get("snippet", {})
            content_details = item.get("contentDetails", {})
            statistics = item.get("statistics", {})
            video_id = item.get("id")

            # Parse duration
            duration_iso = content_details.get("duration", "")
            duration_ms = self._parse_duration_to_ms(duration_iso)

            # Get best thumbnail
            thumbnails = snippet.get("thumbnails", {})
            thumbnail_url = thumbnails.get("maxres", {}).get("url") or \
                            thumbnails.get("high", {}).get("url") or \
                            thumbnails.get("medium", {}).get("url")

            # Queue up the color extraction
            color_tasks.append(self._get_primary_color(thumbnail_url))

            # Build initial result object
            results.append({
                "id": video_id,
                "title": snippet.get("title"),
                "thumbnail": thumbnail_url,
                "channel_title": snippet.get("channelTitle"),
                "published_at": snippet.get("publishedAt"),
                "length_ms": duration_ms,
                "view_count": int(statistics.get("viewCount", 0)),
                "url": f"https://www.youtube.com/watch?v={video_id}",
            })

        # 5. Run all color extraction tasks concurrently
        colors = await asyncio.gather(*color_tasks)

        # 6. Assign colors to results
        for result, color in zip(results, colors):
            result["primary_color"] = color

        return results

    async def _get_primary_color(self, image_url: str) -> str:
        """Downloads the image and calculates the dominant color."""
        if not image_url:
            return "000000"

        try:
            response = await self.client.get(image_url)
            if response.status_code != 200:
                return "000000"

            # Open image with PIL
            image = Image.open(io.BytesIO(response.content))

            # Resize to a smaller size to speed up processing
            image = image.resize((150, 150))

            # Reduce to a palette of 1 color to get the dominant one
            dominant_color = image.quantize(colors=1).convert('RGB').getpixel((0, 0))

            # Convert RGB tuple to Hex string
            return '{:02x}{:02x}{:02x}'.format(*dominant_color)

        except Exception:
            # Fallback to black if anything fails
            return "000000"

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