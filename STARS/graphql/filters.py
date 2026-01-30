# STARS/graphql/filters.py

import strawberry
import strawberry_django
from strawberry import auto
from typing import Optional

from STARS import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from strawberry_django.filters import FilterLookup
from django.db.models import Q, Exists, OuterRef, QuerySet, Value
from django.db.models.functions import Concat
from django.contrib.postgres.search import TrigramSimilarity


def trigram_search(queryset: QuerySet, value: str, *fields) -> tuple[QuerySet, Q]:
    if not value:
        return queryset, Q()

    search_expression = fields[0]
    for field in fields[1:]:
        search_expression = Concat(search_expression, Value(' '), field)

    # Get the model's primary key field name
    model = queryset.model
    pk_field = model._meta.pk.name

    qs = queryset.annotate(
        similarity=TrigramSimilarity(search_expression, value)
    ).filter(
        similarity__gt=0.1
    ).order_by(pk_field, '-similarity').distinct(pk_field)  # ✅ Distinct on primary key

    return qs, Q()



@strawberry_django.filter(models.MusicGenre, lookups=True)
class MusicGenreFilter:
    id: auto
    title: auto
    is_featured: auto


@strawberry_django.filter(models.ProjectGenresOrdered, lookups=True)
class ProjectGenresOrderedFilter:
    id: auto
    position: auto
    project: Optional["ProjectFilter"]
    genre: Optional["MusicGenreFilter"]


@strawberry_django.filter(models.SongGenresOrdered, lookups=True)
class SongGenresOrderedFilter:
    id: auto
    position: auto
    song: Optional["SongFilter"]
    genre: Optional["MusicGenreFilter"]


@strawberry_django.filter(models.ArtistGenresOrdered, lookups=True)
class ArtistGenresOrderedFilter:
    id: auto
    position: auto
    artist: Optional["ArtistFilter"]
    genre: Optional["MusicGenreFilter"]


@strawberry_django.filter(models.PodcastGenre, lookups=True)
class PodcastGenreFilter:
    id: auto
    title: auto
    is_featured: auto


@strawberry_django.filter(models.PodcastGenresOrdered, lookups=True)
class PodcastGenresOrderedFilter:
    id: auto
    position: auto
    podcast: Optional["PodcastFilter"]
    genre: Optional["PodcastGenreFilter"]


@strawberry_django.filter(models.Artist, lookups=True)
class ArtistFilter:
    id: auto
    apple_music_id: auto
    name: auto
    origin: auto
    is_featured: auto
    projects_star_average: auto
    songs_star_average: auto
    music_videos_star_average: auto
    performances_star_average: auto
    covers_star_average: auto
    outfits_star_average: auto

    @strawberry_django.filter_field
    def search(self, queryset: QuerySet, value: str, prefix) -> tuple[QuerySet, Q]:
        return trigram_search(queryset, value, 'name')


@strawberry_django.filter(models.EventSeries, lookups=True)
class EventSeriesFilter:
    id: auto
    name: auto
    is_featured: auto
    series_type: auto

    @strawberry_django.filter_field
    def search(self, queryset: QuerySet, value: str, prefix) -> tuple[QuerySet, Q]:
        return trigram_search(queryset, value, 'name')


@strawberry_django.filter(models.Event, lookups=True)
class EventFilter:
    id: auto
    name: auto
    date: auto
    location: auto
    is_one_time: auto
    is_featured: auto
    series: Optional["EventSeriesFilter"]
    event_type: auto

    reviews_count: auto
    reviews_count_0_5: auto
    reviews_count_1: auto
    reviews_count_1_5: auto
    reviews_count_2: auto
    reviews_count_2_5: auto
    reviews_count_3: auto
    reviews_count_3_5: auto
    reviews_count_4: auto
    reviews_count_4_5: auto
    reviews_count_5: auto
    star_average: auto

    @strawberry_django.filter_field
    def search(self, queryset: QuerySet, value: str, prefix) -> tuple[QuerySet, Q]:
        return trigram_search(queryset, value, 'name', 'location', 'series__name')


@strawberry_django.filter(models.Comment, lookups=True)
class CommentFilter:
    id: auto
    number_of_replies: auto
    replying_to: Optional[FilterLookup["CommentFilter"]]
    review: Optional["ReviewFilter"]
    user: Optional["UserFilter"]
    likes_count: auto
    dislikes_count: auto
    date_created: auto


@strawberry_django.filter(ContentType, lookups=True)
class ContentTypeFilter:
    model: auto


@strawberry_django.filter(models.Review, lookups=True)
class ReviewFilter:
    id: auto
    stars: auto
    title: auto
    text: auto
    user: Optional["UserFilter"]
    comments_count: auto
    likes_count: auto
    dislikes_count: auto
    date_created: auto
    is_latest: auto
    object_id: auto
    content_type: Optional["ContentTypeFilter"]

    @strawberry_django.filter_field
    def search(self, queryset: QuerySet, value: str, prefix) -> tuple[QuerySet, Q]:
        return trigram_search(queryset, value, 'title', 'text', 'user__username')


@strawberry_django.filter(models.SubReview, lookups=True)
class SubReviewFilter:
    id: auto
    topic: auto
    position: auto
    stars: auto


@strawberry_django.filter(models.Cover, lookups=True)
class CoverFilter:
    id: auto
    position: auto
    is_featured: auto

    reviews_count: auto
    reviews_count_0_5: auto
    reviews_count_1: auto
    reviews_count_1_5: auto
    reviews_count_2: auto
    reviews_count_2_5: auto
    reviews_count_3: auto
    reviews_count_3_5: auto
    reviews_count_4: auto
    reviews_count_4_5: auto
    reviews_count_5: auto
    star_average: auto
    is_confirmed: auto


@strawberry_django.filter(models.MusicVideo, lookups=True)
class MusicVideoFilter:
    id: auto
    youtube_id: auto
    number_of_songs: auto
    title: auto
    release_date: auto
    is_featured: auto

    reviews_count: auto
    reviews_count_0_5: auto
    reviews_count_1: auto
    reviews_count_1_5: auto
    reviews_count_2: auto
    reviews_count_2_5: auto
    reviews_count_3: auto
    reviews_count_3_5: auto
    reviews_count_4: auto
    reviews_count_4_5: auto
    reviews_count_5: auto
    star_average: auto

    @strawberry_django.filter_field
    def search(self, queryset: QuerySet, value: str, prefix) -> tuple[QuerySet, Q]:
        return trigram_search(
            queryset, value,
            'title',
            'songs__title',
            'songs__song_artists__artist__name'
        )


@strawberry_django.filter(models.PerformanceVideo, lookups=True)
class PerformanceVideoFilter:
    id: auto
    youtube_id: auto
    event: Optional["EventFilter"]
    number_of_songs: auto
    title: auto
    release_date: auto
    is_featured: auto

    reviews_count: auto
    reviews_count_0_5: auto
    reviews_count_1: auto
    reviews_count_1_5: auto
    reviews_count_2: auto
    reviews_count_2_5: auto
    reviews_count_3: auto
    reviews_count_3_5: auto
    reviews_count_4: auto
    reviews_count_4_5: auto
    reviews_count_5: auto
    star_average: auto

    @strawberry_django.filter_field
    def search(self, queryset: QuerySet, value: str, prefix) -> tuple[QuerySet, Q]:
        return trigram_search(queryset, value, 'title')


@strawberry_django.filter(models.Song, lookups=True)
class SongFilter:
    apple_music_id: auto
    id: auto
    title: auto
    release_date: auto
    is_featured: auto
    song_artists: Optional["SongArtistFilter"]

    reviews_count: auto
    reviews_count_0_5: auto
    reviews_count_1: auto
    reviews_count_1_5: auto
    reviews_count_2: auto
    reviews_count_2_5: auto
    reviews_count_3: auto
    reviews_count_3_5: auto
    reviews_count_4: auto
    reviews_count_4_5: auto
    reviews_count_5: auto
    star_average: auto

    @strawberry_django.filter_field
    def search(self, queryset: QuerySet, value: str, prefix) -> tuple[QuerySet, Q]:
        return trigram_search(queryset, value, 'title', 'song_artists__artist__name')


@strawberry_django.filter(models.SongArtist, lookups=True)
class SongArtistFilter:
    id: auto
    position: auto
    song: Optional["SongFilter"]
    artist: Optional["ArtistFilter"]


@strawberry_django.filter(models.Project, lookups=True)
class ProjectFilter:
    apple_music_id: auto
    id: auto
    title: auto
    length: auto
    release_date: auto
    project_type: auto
    record_label: auto
    is_featured: auto

    reviews_count: auto
    reviews_count_0_5: auto
    reviews_count_1: auto
    reviews_count_1_5: auto
    reviews_count_2: auto
    reviews_count_2_5: auto
    reviews_count_3: auto
    reviews_count_3_5: auto
    reviews_count_4: auto
    reviews_count_4_5: auto
    reviews_count_5: auto
    star_average: auto

    @strawberry_django.filter_field
    def search(self, queryset: QuerySet, value: str, prefix) -> tuple[QuerySet, Q]:
        return trigram_search(
            queryset, value,
            'title',
            'project_artists__artist__name',
            'project_songs__song__title'
        )


@strawberry_django.filter(models.ProjectArtist, lookups=True)
class ProjectArtistFilter:
    id: auto
    position: auto
    project: Optional["ProjectFilter"]
    artist: Optional["ArtistFilter"]


@strawberry_django.filter(models.ProjectSong, lookups=True)
class ProjectSongFilter:
    id: auto
    position: auto
    disc_number: auto
    project: Optional["ProjectFilter"]
    song: Optional["SongFilter"]


@strawberry_django.filter(models.Podcast, lookups=True)
class PodcastFilter:
    id: auto
    apple_podcasts_id: auto
    title: auto
    host: auto
    since: auto
    is_featured: auto

    reviews_count: auto
    reviews_count_0_5: auto
    reviews_count_1: auto
    reviews_count_1_5: auto
    reviews_count_2: auto
    reviews_count_2_5: auto
    reviews_count_3: auto
    reviews_count_3_5: auto
    reviews_count_4: auto
    reviews_count_4_5: auto
    reviews_count_5: auto
    star_average: auto

    @strawberry_django.filter_field
    def search(self, queryset: QuerySet, value: str, prefix) -> tuple[QuerySet, Q]:
        return trigram_search(queryset, value, 'title', 'host')


@strawberry_django.filter(models.Outfit, lookups=True)
class OutfitFilter:
    id: auto
    artist: Optional["ArtistFilter"]
    event: Optional["EventFilter"]
    date: auto
    is_featured: auto

    reviews_count: auto
    reviews_count_0_5: auto
    reviews_count_1: auto
    reviews_count_1_5: auto
    reviews_count_2: auto
    reviews_count_2_5: auto
    reviews_count_3: auto
    reviews_count_3_5: auto
    reviews_count_4: auto
    reviews_count_4_5: auto
    reviews_count_5: auto
    star_average: auto


@strawberry_django.filter(models.Conversation, lookups=True)
class ConversationFilter:
    id: auto


@strawberry_django.filter(models.Message, lookups=True)
class MessageFilter:
    id: auto
    sender: Optional["UserFilter"]
    is_read: auto
    is_delivered: auto


@strawberry_django.filter(models.Profile, lookups=True)
class ProfileFilter:
    id: auto
    user: Optional["UserFilter"]
    has_premium: auto

    reviews_count: auto
    reviews_count_0_5: auto
    reviews_count_1: auto
    reviews_count_1_5: auto
    reviews_count_2: auto
    reviews_count_2_5: auto
    reviews_count_3: auto
    reviews_count_3_5: auto
    reviews_count_4: auto
    reviews_count_4_5: auto
    reviews_count_5: auto

    project_reviews_count: auto
    project_reviews_count_0_5: auto
    project_reviews_count_1: auto
    project_reviews_count_1_5: auto
    project_reviews_count_2: auto
    project_reviews_count_2_5: auto
    project_reviews_count_3: auto
    project_reviews_count_3_5: auto
    project_reviews_count_4: auto
    project_reviews_count_4_5: auto
    project_reviews_count_5: auto

    song_reviews_count: auto
    song_reviews_count_0_5: auto
    song_reviews_count_1: auto
    song_reviews_count_1_5: auto
    song_reviews_count_2: auto
    song_reviews_count_2_5: auto
    song_reviews_count_3: auto
    song_reviews_count_3_5: auto
    song_reviews_count_4: auto
    song_reviews_count_4_5: auto
    song_reviews_count_5: auto

    music_video_reviews_count: auto
    music_video_reviews_count_0_5: auto
    music_video_reviews_count_1: auto
    music_video_reviews_count_1_5: auto
    music_video_reviews_count_2: auto
    music_video_reviews_count_2_5: auto
    music_video_reviews_count_3: auto
    music_video_reviews_count_3_5: auto
    music_video_reviews_count_4: auto
    music_video_reviews_count_4_5: auto
    music_video_reviews_count_5: auto

    performance_video_reviews_count: auto
    performance_video_reviews_count_0_5: auto
    performance_video_reviews_count_1: auto
    performance_video_reviews_count_1_5: auto
    performance_video_reviews_count_2: auto
    performance_video_reviews_count_2_5: auto
    performance_video_reviews_count_3: auto
    performance_video_reviews_count_3_5: auto
    performance_video_reviews_count_4: auto
    performance_video_reviews_count_4_5: auto
    performance_video_reviews_count_5: auto

    cover_reviews_count: auto
    cover_reviews_count_0_5: auto
    cover_reviews_count_1: auto
    cover_reviews_count_1_5: auto
    cover_reviews_count_2: auto
    cover_reviews_count_2_5: auto
    cover_reviews_count_3: auto
    cover_reviews_count_3_5: auto
    cover_reviews_count_4: auto
    cover_reviews_count_4_5: auto
    cover_reviews_count_5: auto

    podcast_reviews_count: auto
    podcast_reviews_count_0_5: auto
    podcast_reviews_count_1: auto
    podcast_reviews_count_1_5: auto
    podcast_reviews_count_2: auto
    podcast_reviews_count_2_5: auto
    podcast_reviews_count_3: auto
    podcast_reviews_count_3_5: auto
    podcast_reviews_count_4: auto
    podcast_reviews_count_4_5: auto
    podcast_reviews_count_5: auto

    outfit_reviews_count: auto
    outfit_reviews_count_0_5: auto
    outfit_reviews_count_1: auto
    outfit_reviews_count_1_5: auto
    outfit_reviews_count_2: auto
    outfit_reviews_count_2_5: auto
    outfit_reviews_count_3: auto
    outfit_reviews_count_3_5: auto
    outfit_reviews_count_4: auto
    outfit_reviews_count_4_5: auto
    outfit_reviews_count_5: auto

    event_reviews_count: auto
    event_reviews_count_0_5: auto
    event_reviews_count_1: auto
    event_reviews_count_1_5: auto
    event_reviews_count_2: auto
    event_reviews_count_2_5: auto
    event_reviews_count_3: auto
    event_reviews_count_3_5: auto
    event_reviews_count_4: auto
    event_reviews_count_4_5: auto
    event_reviews_count_5: auto


@strawberry_django.filter(models.SearchHistory, lookups=True)
class SearchHistoryFilter:
    id: auto
    user: Optional["UserFilter"]
    query: auto
    category: auto
    timestamp: auto


@strawberry_django.filter(User, lookups=True)
class UserFilter:
    id: auto
    username: auto
    email: auto
    first_name: auto
    reviews: Optional["ReviewFilter"]

    @strawberry_django.filter_field
    def search(self, queryset: QuerySet, value: str, prefix) -> tuple[QuerySet, Q]:
        return trigram_search(queryset, value, 'username', 'first_name')


@strawberry_django.filter(models.Report)
class ReportFilter:
    status: auto
    created_at: auto