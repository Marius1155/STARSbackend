import httpx
from typing import Dict, Any, List
from .apple_music_token import get_apple_music_token

APPLE_MUSIC_API_URL = "https://api.music.apple.com/v1"


class AppleMusicService:
    def __init__(self):
        self.client = httpx.AsyncClient()  # reusable async client

    def _prioritize_explicit(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sorts items to prioritize explicit content.
        1. Explicit
        2. Unrated (Standard)
        3. Clean
        """

        def sort_key(item):
            rating = item.get("attributes", {}).get("contentRating")
            if rating == "explicit":
                return 0
            if rating == "clean":
                return 2
            return 1  # Unrated/Unknown

        return sorted(items, key=sort_key)

    async def search_albums(self, term: str, limit: int = 20, country: str = "us") -> List[Dict[str, Any]]:
        url = f"{APPLE_MUSIC_API_URL}/catalog/{country}/search"
        params = {"term": term, "types": "albums", "limit": limit}
        headers = {"Authorization": f"Bearer {get_apple_music_token()}"}
        response = await self.client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        albums = data.get("results", {}).get("albums", {}).get("data", [])
        # Apply the sort to put Explicit albums at the top
        return self._prioritize_explicit(albums)

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
        # We request 'other-versions' to check for explicit alternatives
        params = {"include": "other-versions"}
        headers = {"Authorization": f"Bearer {get_apple_music_token()}"}

        response = await self.client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            return {}

        album = data[0]
        attributes = album.get("attributes", {})

        # If the fetched album is Clean, try to find the Explicit version
        if attributes.get("contentRating") == "clean":
            other_versions = album.get("relationships", {}).get("other-versions", {}).get("data", [])
            for version in other_versions:
                if version.get("attributes", {}).get("contentRating") == "explicit":
                    # Found explicit version! Recursively fetch that one instead.
                    return await self.get_album_with_songs(version["id"], country)

        return album

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

    async def close(self):
        await self.client.aclose()