import httpx
from typing import List, Dict, Any

ITUNES_API_URL = "https://itunes.apple.com/search"


class iTunesService:
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def search_podcasts(self, term: str, limit: int = 20) -> List[Dict[str, Any]]:
        params = {
            "term": term,
            "media": "podcast",
            "entity": "podcast",
            "limit": limit
        }
        # The iTunes API is public, so no headers/tokens needed
        response = await self.client.get(ITUNES_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])

    async def get_podcast_details(self, collection_id: str) -> Dict[str, Any]:
        """Fetch details for a specific podcast by its ID (lookup)."""
        url = "https://itunes.apple.com/lookup"
        params = {"id": collection_id}

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        return results[0] if results else {}

    async def close(self):
        await self.client.aclose()