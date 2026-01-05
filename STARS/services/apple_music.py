import httpx
import re
from typing import Dict, Any, List
from .apple_music_token import get_apple_music_token

APPLE_MUSIC_API_URL = "https://api.music.apple.com/v1"


class AppleMusicService:
    def __init__(self):
        self.client = httpx.AsyncClient()  # reusable async client

    def _fix_censored_title(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempts to uncensor the album title using the URL slug if the name contains asterisks.
        Example:
        Name: "S********"
        URL: "https://music.apple.com/us/album/starfucker/..."
        Result Name: "Starfucker"
        """
        if item.get("type") != "albums":
            return item

        attributes = item.get("attributes", {})
        name = attributes.get("name", "")

        # Only attempt to fix if it looks censored
        if "*" in name:
            url = attributes.get("url", "")
            # Extract slug from URL: /album/slug-name/id
            match = re.search(r"/album/([^/]+)/", url)
            if match:
                slug = match.group(1)
                # Convert slug to Title Case (e.g., "starfucker" -> "Starfucker", "my-album" -> "My Album")
                clean_title = slug.replace("-", " ").title()
                item["attributes"]["name"] = clean_title

        return item

    def _filter_and_deduplicate(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        1. Fixes censored titles.
        2. Groups albums by (Artist, Name).
        3. Keeps only the 'best' version (Explicit > Standard > Clean).
        """
        # 1. Fix titles first so we can match "S********" (Clean) with "Starfucker" (Explicit)
        processed_items = [self._fix_censored_title(item) for item in items]

        grouped: Dict[tuple, List[Dict[str, Any]]] = {}

        for item in processed_items:
            attrs = item.get("attributes", {})
            # Create a key based on Artist and Album Name to identify duplicates
            artist = attrs.get("artistName", "").lower().strip()
            name = attrs.get("name", "").lower().strip()

            key = (artist, name)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(item)

        results = []
        for key, group in grouped.items():
            # 2. Sort priority: Explicit (0) > Standard/Unrated (1) > Clean (2)
            def priority(i):
                rating = i.get("attributes", {}).get("contentRating")
                if rating == "explicit":
                    return 0
                if rating == "clean":
                    return 2
                return 1  # Unrated or Standard

            group.sort(key=priority)

            # 3. Pick the top one.
            # If an explicit version exists (index 0), the clean version (index > 0) is ignored completely.
            results.append(group[0])

        return results

    async def search_albums(self, term: str, limit: int = 20, country: str = "us") -> List[Dict[str, Any]]:
        url = f"{APPLE_MUSIC_API_URL}/catalog/{country}/search"
        params = {"term": term, "types": "albums", "limit": limit}
        headers = {"Authorization": f"Bearer {get_apple_music_token()}"}

        response = await self.client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        albums = data.get("results", {}).get("albums", {}).get("data", [])
        return self._filter_and_deduplicate(albums)

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
        # Request 'other-versions' to check for explicit alternatives
        params = {"include": "other-versions"}
        headers = {"Authorization": f"Bearer {get_apple_music_token()}"}

        response = await self.client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            return {}

        album = data[0]
        attributes = album.get("attributes", {})

        # If Clean, try to switch to Explicit via relationships
        if attributes.get("contentRating") == "clean":
            other_versions = album.get("relationships", {}).get("other-versions", {}).get("data", [])
            for version in other_versions:
                if version.get("attributes", {}).get("contentRating") == "explicit":
                    # Recursively fetch the explicit version
                    return await self.get_album_with_songs(version["id"], country)

        # Fix title if it's still censored (even if it's the explicit version)
        return self._fix_censored_title(album)

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

        # We don't use _filter_and_deduplicate here as it is optimized for Albums (URL slug logic),
        # but you could implement similar song-specific logic if needed.
        # For now, we return the raw list or just sort them if you prefer.
        return data.get("data", [])

    async def close(self):
        await self.client.aclose()