import httpx
from typing import Dict, Any, List
from .apple_music_token import get_apple_music_token

APPLE_MUSIC_API_URL = "https://api.music.apple.com/v1"

class AppleMusicService:
    def __init__(self):
        self.client = httpx.AsyncClient()  # reusable async client

    async def search_albums(self, term: str, limit: int = 20, country: str = "us") -> List[Dict[str, Any]]:
        """Search Apple Music albums by keyword asynchronously."""
        url = f"{APPLE_MUSIC_API_URL}/catalog/{country}/search"
        params = {"term": term, "types": "albums", "limit": limit}
        headers = {"Authorization": f"Bearer {get_apple_music_token()}"}

        response = await self.client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("results", {}).get("albums", {}).get("data", [])

    async def close(self):
        """Close the async client when done."""
        await self.client.aclose()