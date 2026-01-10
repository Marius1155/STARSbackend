"""
Caching utilities for STARS app.
Provides helpers for caching GraphQL queries and common patterns.
"""
from django.core.cache import cache
from functools import wraps
import hashlib
import json
from typing import Optional, Any, Callable
from asgiref.sync import sync_to_async


def make_cache_key(prefix: str, **kwargs) -> str:
    """
    Generate a consistent cache key from prefix and parameters.

    Example:
        make_cache_key("podcast_search", query="Joe Rogan", page=1)
        → "podcast_search:query=Joe Rogan:page=1:hash_abc123"
    """
    # Sort kwargs for consistency
    sorted_params = sorted(kwargs.items())
    param_str = ":".join(f"{k}={v}" for k, v in sorted_params)

    # Create hash of parameters for uniqueness
    param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]

    return f"{prefix}:{param_str}:{param_hash}"


def cache_graphql_query(
        key_prefix: str,
        timeout: int = 300,  # 5 minutes default
        key_params: Optional[list] = None
):
    """
    Decorator to cache GraphQL query results.

    Usage:
        @cache_graphql_query("trending_podcasts", timeout=600)
        async def resolve_trending_podcasts(self, info):
            # expensive database query
            return podcasts
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract parameters for cache key
            cache_params = {}
            if key_params:
                for param in key_params:
                    if param in kwargs:
                        cache_params[param] = kwargs[param]

            # Generate cache key
            cache_key = make_cache_key(key_prefix, **cache_params)

            # Try to get from cache
            cached_result = await sync_to_async(cache.get)(cache_key)
            if cached_result is not None:
                return cached_result

            # Cache miss - execute function
            result = await func(*args, **kwargs)

            # Store in cache
            await sync_to_async(cache.set)(cache_key, result, timeout)

            return result

        return wrapper

    return decorator


async def get_cached(key: str) -> Optional[Any]:
    """Get a value from cache asynchronously."""
    return await sync_to_async(cache.get)(key)


async def set_cached(key: str, value: Any, timeout: int = 300) -> None:
    """Set a value in cache asynchronously."""
    await sync_to_async(cache.set)(key, value, timeout)


async def delete_cached(key: str) -> None:
    """Delete a value from cache asynchronously."""
    await sync_to_async(cache.delete)(key)


async def invalidate_pattern(pattern: str) -> None:
    """
    Invalidate all cache keys matching a pattern.

    Example:
        await invalidate_pattern("podcast:*")  # Clear all podcast caches
    """
    from django_redis import get_redis_connection

    def _delete_pattern():
        conn = get_redis_connection("default")
        keys = conn.keys(f"stars:{pattern}")
        if keys:
            conn.delete(*keys)

    await sync_to_async(_delete_pattern)()


# Cache key constants
class CacheKeys:
    """Centralized cache key definitions."""

    # Search
    PODCAST_SEARCH = "podcast_search"
    MUSIC_SEARCH = "music_search"

    # Detail pages
    PODCAST_DETAIL = "podcast_detail"
    MUSIC_VIDEO_DETAIL = "music_video_detail"
    PERFORMANCE_VIDEO_DETAIL = "performance_video_detail"
    PROJECT_DETAIL = "project_detail"
    ARTIST_DETAIL = "artist_detail"
    OUTFIT_DETAIL = "outfit_detail"
    EVENT_DETAIL = "events_detail"
    EVENT_SERIES_DETAIL = "event_series_detail"

    # Aggregations
    PODCAST_STATS = "podcast_stats"
    ARTIST_STATS = "artist_stats"

    # Lists
    TRENDING_PODCASTS = "trending_podcasts"
    TRENDING_MUSIC = "trending_music"
    TOP_ARTISTS = "top_artists"

    # Genres
    PODCAST_GENRES = "podcast_genres"
    MUSIC_GENRES = "music_genres"