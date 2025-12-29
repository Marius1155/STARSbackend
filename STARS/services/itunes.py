import httpx
import asyncio
from typing import List, Dict, Any

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

    async def close(self):
        await self.client.aclose()