import httpx
import asyncio
from typing import List, Dict, Any
import xml.etree.ElementTree as ET

ITUNES_API_URL = "https://itunes.apple.com/search"
ITUNES_LOOKUP_URL = "https://itunes.apple.com/lookup"

class iTunesService:
    def __init__(self):
        # 30s timeout because bulk fetching can be slow
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search_podcasts(self, term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Standard search for user queries."""
        params = {
            "term": term,
            "media": "podcast",
            "entity": "podcast",
            "limit": limit
        }
        try:
            response = await self.client.get(ITUNES_API_URL, params=params)
            response.raise_for_status()
            return response.json().get("results", [])
        except Exception as e:
            print(f"Error searching podcasts: {e}")
            return []

    async def get_podcasts_by_genre(self, genre_id: int, limit: int = 200) -> List[Dict[str, Any]]:
        """Fetches top podcasts for a specific genre ID."""
        params = {
            "term": "podcast",
            "genreId": genre_id,
            "media": "podcast",
            "entity": "podcast",
            "limit": limit
        }
        try:
            response = await self.client.get(ITUNES_API_URL, params=params)
            response.raise_for_status()
            return response.json().get("results", [])
        except Exception:
            return []

    async def lookup_podcast(self, apple_podcasts_id: str) -> Dict[str, Any]:
        """Fetches a single podcast's details by ID."""
        params = {"id": apple_podcasts_id}
        try:
            response = await self.client.get(ITUNES_LOOKUP_URL, params=params)
            response.raise_for_status()
            results = response.json().get("results", [])
            return results[0] if results else {}
        except Exception:
            return {}

    async def fetch_description_from_rss(self, feed_url: str) -> str:
        """Fetches the RSS feed and extracts the podcast description."""
        if not feed_url:
            return ""
        try:
            response = await self.client.get(feed_url)
            response.raise_for_status()

            root = ET.fromstring(response.text)
            channel = root.find("channel")
            if channel is None:
                return ""

            # Apple specific tag usually has the best description
            namespaces = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
            summary = channel.find("itunes:summary", namespaces)
            if summary is not None and summary.text:
                return summary.text.strip()

            # Fallback to standard RSS description
            description = channel.find("description")
            if description is not None and description.text:
                return description.text.strip()

            return ""
        except Exception as e:
            print(f"Error parsing RSS description: {e}")
            return ""

    async def close(self):
        await self.client.aclose()