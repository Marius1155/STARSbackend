"""
Signal handlers for cache invalidation.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from STARS import models
from STARS.utils.cache import invalidate_pattern
from asgiref.sync import async_to_sync


@receiver([post_save, post_delete], sender=models.Artist)
@receiver([post_save, post_delete], sender=models.Project)
@receiver([post_save, post_delete], sender=models.Song)
@receiver([post_save, post_delete], sender=models.MusicVideo)
@receiver([post_save, post_delete], sender=models.PerformanceVideo)
def invalidate_music_search_cache(sender, instance, **kwargs):
    """Clear music search cache when music content changes."""
    async_to_sync(invalidate_pattern)("music_search*")


'''@receiver([post_save, post_delete], sender=models.MusicGenre)
def invalidate_music_genres_cache(sender, instance, **kwargs):
    """Clear genre cache when genres change."""
    async_to_sync(invalidate_pattern)("music_genres*")'''


'''@receiver([post_save, post_delete], sender=models.PodcastGenre)
def invalidate_podcast_genres_cache(sender, instance, **kwargs):
    """Clear genre cache when genres change."""
    async_to_sync(invalidate_pattern)("podcast_genres*")'''

@receiver([post_save, post_delete], sender=models.Podcast)
def invalidate_podcast_cache(sender, instance, **kwargs):
    """Clear podcast caches when a podcast changes."""
    async_to_sync(invalidate_pattern)(f"podcast_search*")  # Podcasts appear in search