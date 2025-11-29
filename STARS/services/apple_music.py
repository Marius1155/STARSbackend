import httpx
from typing import Dict, Any, List
from .apple_music_token import get_apple_music_token

APPLE_MUSIC_API_URL = "https://api.music.apple.com/v1"


class AppleMusicService:
    def __init__(self):
        self.client = httpx.AsyncClient()  # reusable async client

    async def search_albums(self, term: str, limit: int = 20, country: str = "us") -> List[Dict[str, Any]]:
        url = f"{APPLE_MUSIC_API_URL}/catalog/{country}/search"
        params = {"term": term, "types": "albums", "limit": limit}
        headers = {"Authorization": f"Bearer {get_apple_music_token()}"}
        response = await self.client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("results", {}).get("albums", {}).get("data", [])

    async def search_artists(self, term: str, limit: int = 20, country: str = "us") -> List[Dict[str, Any]]:
        url = f"{APPLE_MUSIC_API_URL}/catalog/{country}/search"
        params = {"term": term, "types": "artists", "limit": limit}
        headers = {"Authorization": f"Bearer {get_apple_music_token()}"}
        response = await self.client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("results", {}).get("artists", {}).get("data", [])

    async def get_album_with_songs(self, album_id: str, country: str = "us") -> Dict[str, Any]:
        url = f"{APPLE_MUSIC_API_URL}/catalog/{country}/albums/{album_id}"
        headers = {"Authorization": f"Bearer {get_apple_music_token()}"}
        response = await self.client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])[0]

    async def get_artist(self, href: str) -> Dict[str, Any]:
        url = f"https://api.music.apple.com{href}"
        headers = {"Authorization": f"Bearer {get_apple_music_token()}"}
        response = await self.client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()["data"][0]

    async def get_artist_by_id(self, artist_id: str, country: str = "us") -> Dict[str, Any]:
        url = f"{APPLE_MUSIC_API_URL}/catalog/{country}/artists/{artist_id}"
        headers = {"Authorization": f"Bearer {get_apple_music_token()}"}
        response = await self.client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])[0]

    async def get_song(self, href: str) -> Dict[str, Any]:
        if not href:
            return {}

        url = f"https://api.music.apple.com{href}"
        headers = {"Authorization": f"Bearer {get_apple_music_token()}"}
        response = await self.client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])[0] if data.get("data") else {}

    async def get_artist_top_songs(self, artist_id: str, limit: int = 10, country: str = "us") -> List[Dict[str, Any]]:
        url = f"{APPLE_MUSIC_API_URL}/catalog/{country}/artists/{artist_id}/view/top-songs"
        params = {"limit": limit}
        headers = {"Authorization": f"Bearer {get_apple_music_token()}"}

        response = await self.client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        return data.get("data", [])

    async def close(self):
        await self.client.aclose()