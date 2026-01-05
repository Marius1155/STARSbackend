import httpx
from typing import Dict, Any, List
from .apple_music_token import get_apple_music_token

APPLE_MUSIC_API_URL = "https://api.music.apple.com/v1"


class AppleMusicService:
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def get_albums_by_ids(self, album_ids: List[str], country: str = "us") -> List[Dict[str, Any]]:
        """
        Bulk fetches album details.
        We include 'other-versions' to find explicit counterparts for clean albums.
        """
        if not album_ids:
            return []

        # Join IDs with comma (limit is usually 100, our search limit is small enough)
        ids_str = ",".join(album_ids)
        url = f"{APPLE_MUSIC_API_URL}/catalog/{country}/albums"
        params = {"ids": ids_str, "include": "other-versions"}
        headers = {"Authorization": f"Bearer {get_apple_music_token()}"}

        response = await self.client.get(url, headers=headers, params=params)
        # We don't raise status here to avoid crashing the whole search if one ID fails,
        # but usually for a valid search list it works fine.
        if response.status_code != 200:
            return []

        return response.json().get("data", [])

    def _process_albums(self, albums: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicates and prioritizes Explicit versions.
        If a Clean album has an Explicit 'other-version', we prefer the Explicit one.
        """
        # Map to store the best version of each album (keyed by Artist + Album Name)
        # Using a dictionary automatically handles basic deduplication
        processed_map: Dict[tuple, Dict[str, Any]] = {}

        for album in albums:
            attributes = album.get("attributes", {})

            # 1. Check if this is a Clean album with an Explicit alternative
            if attributes.get("contentRating") == "clean":
                other_versions = album.get("relationships", {}).get("other-versions", {}).get("data", [])
                explicit_candidate = None

                for version in other_versions:
                    if version.get("attributes", {}).get("contentRating") == "explicit":
                        explicit_candidate = version
                        break

                # If we found an explicit version in the relationships, USE IT.
                # Note: The 'other-versions' relationship usually contains the full attributes
                # needed for a list view (Name, Artist, Artwork).
                if explicit_candidate:
                    album = explicit_candidate
                    attributes = album.get("attributes", {})

            # 2. Create a unique key for deduplication
            artist = attributes.get("artistName", "").lower().strip()
            name = attributes.get("name", "").lower().strip()
            key = (artist, name)

            # 3. Decision Logic:
            # If we haven't seen this album, add it.
            # If we HAVE seen it, only replace it if the new one is Explicit and the old one wasn't.
            if key not in processed_map:
                processed_map[key] = album
            else:
                existing_rating = processed_map[key].get("attributes", {}).get("contentRating")
                new_rating = attributes.get("contentRating")

                if existing_rating != "explicit" and new_rating == "explicit":
                    processed_map[key] = album

        # Convert back to list
        return list(processed_map.values())

    async def search_albums(self, term: str, limit: int = 20, country: str = "us") -> List[Dict[str, Any]]:
        # 1. Perform the Search
        url = f"{APPLE_MUSIC_API_URL}/catalog/{country}/search"
        params = {"term": term, "types": "albums", "limit": limit}
        headers = {"Authorization": f"Bearer {get_apple_music_token()}"}

        response = await self.client.get(url, headers=headers, params=params)
        response.raise_for_status()
        search_data = response.json()

        raw_albums = search_data.get("results", {}).get("albums", {}).get("data", [])
        if not raw_albums:
            return []

        # 2. Extract IDs from search results
        album_ids = [album["id"] for album in raw_albums]

        # 3. Bulk Fetch full details (Uncensored metadata + Relationships)
        # This fixes "S R" because the direct resource endpoint is authoritative.
        detailed_albums = await self.get_albums_by_ids(album_ids, country=country)

        # 4. Filter and Deduplicate (Swap Clean for Explicit)
        # This fixes flickering because we return the final list.
        return self._process_albums(detailed_albums)

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
        # Include 'other-versions' to handle direct lookups of clean IDs
        params = {"include": "other-versions"}
        headers = {"Authorization": f"Bearer {get_apple_music_token()}"}

        response = await self.client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            return {}

        album = data[0]
        attributes = album.get("attributes", {})

        # If Clean, try to switch to Explicit
        if attributes.get("contentRating") == "clean":
            other_versions = album.get("relationships", {}).get("other-versions", {}).get("data", [])
            for version in other_versions:
                if version.get("attributes", {}).get("contentRating") == "explicit":
                    # Recursive call for the explicit version
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