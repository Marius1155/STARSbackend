"""
Signal handlers for cache invalidation and popularity scoring.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from STARS import models
from STARS.utils.cache import invalidate_pattern
from asgiref.sync import async_to_sync
from django.db.models import Count, Q, F
from django.utils import timezone
from datetime import timedelta
from django.contrib.contenttypes.models import ContentType

@receiver([post_save, post_delete], sender=models.Artist)
@receiver([post_save, post_delete], sender=models.Project)
@receiver([post_save, post_delete], sender=models.Song)
@receiver([post_save, post_delete], sender=models.MusicVideo)
@receiver([post_save, post_delete], sender=models.PerformanceVideo)
def invalidate_music_search_cache(sender, instance, **kwargs):
    """Clear music search cache when music content changes."""
    async_to_sync(invalidate_pattern)("music_search*")

@receiver([post_save, post_delete], sender=models.Podcast)
def invalidate_podcast_cache(sender, instance, **kwargs):
    """Clear podcast caches when a podcast changes."""
    async_to_sync(invalidate_pattern)(f"podcast_search*")

@receiver(post_save, sender=models.Review)
def boost_popularity(sender, instance, created, **kwargs):
    if created:
        try:
            target = instance.content_object
            if hasattr(target, 'popularity_score'):
                target.popularity_score = F('popularity_score') + 11
                target.save(update_fields=['popularity_score'])
        except Exception:
            pass

@receiver(post_delete, sender=models.Review)
def decrease_popularity(sender, instance, **kwargs):
    try:
        target = instance.content_object
        if hasattr(target, 'popularity_score'):
            target.popularity_score = F('popularity_score') - 11
            target.save(update_fields=['popularity_score'])
    except Exception:
        pass