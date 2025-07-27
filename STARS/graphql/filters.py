# STARS/graphql/filters.py

import strawberry
import strawberry_django
from strawberry import auto
from typing import Optional

# Import all the models you want to create filters for
from STARS import models
from django.contrib.auth.models import User

# This decorator tells Strawberry to create a GraphQL input type
# based on the model, which can be used for filtering.
# The `lookups=True` argument automatically enables advanced
# filtering options like 'icontains', 'gt' (greater than), etc.

@strawberry_django.filter(models.Artist, lookups=True)
class ArtistFilter:
    id: auto
    name: auto
    origin: auto
    is_featured: auto

@strawberry_django.filter(models.EventSeries, lookups=True)
class EventSeriesFilter:
    id: auto
    name: auto
    is_featured: auto

@strawberry_django.filter(models.Event, lookups=True)
class EventFilter:
    id: auto
    name: auto
    date: auto
    location: auto
    is_one_time: auto
    is_featured: auto
    series: Optional["EventSeriesFilter"]

@strawberry_django.filter(models.Review, lookups=True)
class ReviewFilter:
    id: auto
    stars: auto
    user: Optional["UserFilter"]
    date_created: auto
    is_latest: auto

@strawberry_django.filter(models.SubReview, lookups=True)
class SubReviewFilter:
    id: auto
    topic: auto
    stars: auto

@strawberry_django.filter(models.Cover, lookups=True)
class CoverFilter:
    id: auto
    is_featured: auto

@strawberry_django.filter(models.MusicVideo, lookups=True)
class MusicVideoFilter:
    id: auto
    title: auto
    release_date: auto
    is_featured: auto

@strawberry_django.filter(models.Song, lookups=True)
class SongFilter:
    id: auto
    title: auto
    release_date: auto
    is_featured: auto

@strawberry_django.filter(models.SongArtist, lookups=True)
class SongArtistFilter:
    id: auto
    song: Optional["SongFilter"]
    artist: Optional["ArtistFilter"]

@strawberry_django.filter(models.Project, lookups=True)
class ProjectFilter:
    id: auto
    title: auto
    release_date: auto
    project_type: auto
    is_featured: auto

@strawberry_django.filter(models.ProjectArtist, lookups=True)
class ProjectArtistFilter:
    id: auto
    project: Optional["ProjectFilter"]
    artist: Optional["ArtistFilter"]

@strawberry_django.filter(models.ProjectSong, lookups=True)
class ProjectSongFilter:
    id: auto
    project: Optional["ProjectFilter"]
    song: Optional["SongFilter"]

@strawberry_django.filter(models.Podcast, lookups=True)
class PodcastFilter:
    id: auto
    title: auto
    since: auto
    is_featured: auto

@strawberry_django.filter(models.Outfit, lookups=True)
class OutfitFilter:
    id: auto
    artist: Optional["ArtistFilter"]
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

@strawberry_django.filter(models.Profile, lookups=True)
class ProfileFilter:
    id: auto
    user: Optional["UserFilter"]
    has_premium: auto

@strawberry_django.filter(User, lookups=True)
class UserFilter:
    id: auto
    username: auto
    email: auto
    first_name: auto
    last_name: auto
