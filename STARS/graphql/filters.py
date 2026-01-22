# STARS/graphql/filters.py

import strawberry
import strawberry_django
from strawberry import auto
from typing import Optional

# Import all the models you want to create filters for
from STARS import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from strawberry_django.filters import FilterLookup
from django.db.models import Q, Exists, OuterRef, QuerySet
from STARS.models import ProjectArtist, ProjectSong


# For Relay Nodes, the `id` filter should accept a simple integer,
# which the resolver will then use to find the object.

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
    id: auto # This will correctly resolve to an Int lookup
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
        if value:
            return queryset.filter(Q(name__icontains=value)), Q()
        return queryset, Q()

@strawberry_django.filter(models.EventSeries, lookups=True)
class EventSeriesFilter:
    id: auto
    name: auto
    is_featured: auto
    series_type: auto

    @strawberry_django.filter_field
    def search(self, queryset: QuerySet, value: str, prefix) -> tuple[QuerySet, Q]:
        if value:
            return queryset.filter(Q(name__icontains=value)), Q()
        return queryset, Q()

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

    @strawberry_django.filter_field
    def search(self, queryset: QuerySet, value: str, prefix) -> tuple[QuerySet, Q]:
        if value:
            series_exists = Exists(
                models.EventSeries.objects.filter(
                    events=OuterRef('pk'),
                    name__icontains=value
                )
            )

            return queryset.filter(
                Q(name__icontains=value) |
                Q(location__icontains=value) |
                Q(series_exists)
            ), Q()
        return queryset, Q()

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

@strawberry_django.filter(models.MusicVideo, lookups=True)
class MusicVideoFilter:
    id: auto
    youtube_id: auto
    number_of_songs: auto
    title: auto
    release_date: auto
    is_featured: auto

    @strawberry_django.filter_field
    def search(self, queryset: QuerySet, value: str, prefix) -> tuple[QuerySet, Q]:
        if value:
            song_match_exists = Exists(
                models.Song.objects.filter(
                    music_videos=OuterRef('pk'),
                    title__icontains=value
                )
            )

            artist_match_exists = Exists(
                models.Artist.objects.filter(
                    song_artists__song__music_videos=OuterRef('pk'),
                    name__icontains=value
                )
            )

            return queryset.filter(
                Q(title__icontains=value) |
                Q(song_match_exists) |
                Q(artist_match_exists)
            ), Q()
        return queryset, Q()


@strawberry_django.filter(models.PerformanceVideo, lookups=True)
class PerformanceVideoFilter:
    id: auto
    youtube_id: auto
    event: Optional["EventFilter"]
    number_of_songs: auto
    title: auto
    release_date: auto
    is_featured: auto

    @strawberry_django.filter_field
    def search(self, queryset: QuerySet, value: str, prefix) -> tuple[QuerySet, Q]:
        if value:
            return queryset.filter(Q(title__icontains=value)), Q()

        return queryset, Q()


@strawberry_django.filter(models.Song, lookups=True)
class SongFilter:
    apple_music_id: auto
    id: auto
    title: auto
    release_date: auto
    is_featured: auto

    # Allow filtering by specific artist fields (e.g. artist.name)
    song_artists: Optional["SongArtistFilter"]

    @strawberry_django.filter_field
    def search(self, queryset: QuerySet, value: str, prefix) -> tuple[QuerySet, Q]:
        if value:
            # Check if song title matches
            title_match = Q(title__icontains=value)

            # Efficiently check for artist matches associated with this song
            artist_exists = Exists(
                models.SongArtist.objects.filter(
                    song=OuterRef('pk'),
                    artist__name__icontains=value
                )
            )

            # Return the filtered queryset and an empty Q() object
            return queryset.filter(title_match | artist_exists), Q()

        return queryset, Q()

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

    @strawberry_django.filter_field
    def search(self, queryset: QuerySet, value: str, prefix) -> tuple[QuerySet, Q]:  # Change return type hint
        if value:
            title_match = Q(title__icontains=value)

            artist_exists = Exists(
                ProjectArtist.objects.filter(
                    project=OuterRef('pk'),
                    artist__name__icontains=value
                )
            )

            song_exists = Exists(
                ProjectSong.objects.filter(
                    project=OuterRef('pk'),
                    song__title__icontains=value
                )
            )

            return queryset.filter(title_match | Q(artist_exists) | Q(song_exists)), Q()

        return queryset, Q()

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

    @strawberry_django.filter_field
    def search(self, queryset: QuerySet, value: str, prefix) -> tuple[QuerySet, Q]:
        if value:
            return queryset.filter(
                Q(title__icontains=value) | Q(host__icontains=value)
            ), Q()
        return queryset, Q()

@strawberry_django.filter(models.Outfit, lookups=True)
class OutfitFilter:
    id: auto
    artist: Optional["ArtistFilter"]
    event: Optional["EventFilter"]
    date: auto
    is_featured: auto

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
    last_name: auto
    reviews: Optional["ReviewFilter"]
