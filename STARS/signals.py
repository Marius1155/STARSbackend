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

@receiver([post_save, post_delete], sender=models.Project)
def invalidate_project_cache(sender, instance, **kwargs):
    """Clear project caches when a project changes."""
    async_to_sync(invalidate_pattern)(f"project_detail*")
    async_to_sync(invalidate_pattern)(f"music_search*")  # Projects appear in search

@receiver([post_save, post_delete], sender=models.Artist)
def invalidate_artist_cache(sender, instance, **kwargs):
    """Clear artist caches when an artist changes."""
    async_to_sync(invalidate_pattern)(f"artist_detail*")
    async_to_sync(invalidate_pattern)(f"music_search*")  # Artists appear in search

@receiver([post_save, post_delete], sender=models.Podcast)
def invalidate_podcast_cache(sender, instance, **kwargs):
    """Clear podcast caches when a podcast changes."""
    async_to_sync(invalidate_pattern)(f"podcast_detail*")
    async_to_sync(invalidate_pattern)(f"podcast_search*")  # Podcasts appear in search

@receiver([post_save, post_delete], sender=models.MusicVideo)
def invalidate_music_video_cache(sender, instance, **kwargs):
    """Clear music video caches when a music video changes."""
    async_to_sync(invalidate_pattern)(f"music_video_detail*")
    async_to_sync(invalidate_pattern)(f"music_search*")  # Music videos appear in search

@receiver([post_save, post_delete], sender=models.PerformanceVideo)
def invalidate_performance_video_cache(sender, instance, **kwargs):
    """Clear performance video caches when a performance video changes."""
    async_to_sync(invalidate_pattern)(f"performance_video_detail*")
    async_to_sync(invalidate_pattern)(f"music_search*")  # Performance videos appear in search

@receiver([post_save, post_delete], sender=models.Outfit)
def invalidate_outfit_cache(sender, instance, **kwargs):
    """Clear outfit caches when an outfit changes."""
    async_to_sync(invalidate_pattern)(f"outfit_detail*")

@receiver([post_save, post_delete], sender=models.Event)
def invalidate_event_cache(sender, instance, **kwargs):
    """Clear event caches when an event changes."""
    async_to_sync(invalidate_pattern)(f"event_detail*")

@receiver([post_save, post_delete], sender=models.EventSeries)
def invalidate_event_series_cache(sender, instance, **kwargs):
    """Clear event series caches when an event series changes."""
    async_to_sync(invalidate_pattern)(f"event_series_detail*")