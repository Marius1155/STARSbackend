from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.contenttypes.models import ContentType
from STARS import models


class Command(BaseCommand):
    help = 'Recalculates popularity: (Total Reviews) + (10 * Reviews in last 7 days)'

    def handle(self, *args, **options):
        self.stdout.write("Starting popularity refresh...")

        # 1. Setup the time window
        recent_threshold = timezone.now() - timedelta(days=7)

        target_models = [
            models.Song,
            models.Project,
            models.MusicVideo,
            models.PerformanceVideo,
            models.Event,
            models.Outfit,
            models.Podcast,
            models.Cover
        ]

        for model_class in target_models:
            model_name = model_class.__name__
            self.stdout.write(f"Refreshing {model_name}...")

            # 2. efficient Database Annotation
            # We calculate both counts in a single pass for every object in the table
            qs = model_class.objects.annotate(
                real_total=Count('reviews'),
                real_recent=Count(
                    'reviews',
                    filter=Q(reviews__date_created__gte=recent_threshold)
                )
            )

            batch = []

            # 3. Compare and Queue Updates
            for obj in qs:
                # The Formula:
                correct_score = obj.real_total + (obj.real_recent * 10)

                # Only update if the Signals drifted from the truth
                # (or if reviews aged out of the 7-day window)
                if obj.popularity_score != correct_score:
                    obj.popularity_score = correct_score
                    batch.append(obj)

                    # Safety check for batch size (optional, good for huge DBs)
                    if len(batch) > 1000:
                        model_class.objects.bulk_update(batch, ['popularity_score'])
                        batch = []

            # 4. Final Commit
            if batch:
                model_class.objects.bulk_update(batch, ['popularity_score'])
                self.stdout.write(f" -> Updated {len(batch)} items.")
            else:
                self.stdout.write(" -> No changes needed.")

        self.stdout.write(self.style.SUCCESS("Popularity refresh complete."))