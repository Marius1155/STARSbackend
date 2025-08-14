import strawberry
import strawberry_django
from typing import List, Optional
from STARS import models
from django.contrib.auth.models import User as DjangoUser

# Import your filters to use them in the fields
from . import filters


@strawberry_django.type(models.Artist, fields="__all__", pagination=True)
class Artist:
    song_artists: List["SongArtist"] = strawberry_django.field(filters=filters.SongArtistFilter)
    project_artists: List["ProjectArtist"] = strawberry_django.field(filters=filters.ProjectArtistFilter)
    outfits: List["Outfit"] = strawberry_django.field(filters=filters.OutfitFilter)
    podcasts: List["Podcast"] = strawberry_django.field(filters=filters.PodcastFilter)


@strawberry_django.type(models.EventSeries, fields="__all__", pagination=True)
class EventSeries:
    events: List["Event"] = strawberry_django.field(filters=filters.EventFilter)


@strawberry_django.type(models.Event, fields="__all__", pagination=True)
class Event:
    series: "EventSeries"
    reviews: List["Review"] = strawberry_django.field(filters=filters.ReviewFilter)
    outfits: List["Outfit"] = strawberry_django.field(filters=filters.OutfitFilter)


@strawberry_django.type(DjangoUser, fields=["id", "username", "email", "first_name", "is_staff", "is_superuser"], pagination=True)
class User:
    profile: "Profile"
    conversations: List["Conversation"] = strawberry_django.field(filters=filters.ConversationFilter)
    reviews: List["Review"] = strawberry_django.field(filters=filters.ReviewFilter)


@strawberry_django.type(models.Review, fields="__all__", pagination=True)
class Review:
    user: "User"
    content_object: "Reviewable"
    subreviews: List["SubReview"] = strawberry_django.field(filters=filters.SubReviewFilter)


@strawberry_django.type(models.SubReview, fields="__all__", pagination=True)
class SubReview:
    review: "Review"


@strawberry_django.type(models.Cover, fields="__all__", pagination=True)
class Cover:
    content_object: "Coverable"
    reviews: List["Review"] = strawberry_django.field(filters=filters.ReviewFilter)


@strawberry_django.type(models.MusicVideo, fields="__all__", pagination=True)
class MusicVideo:
    songs: List["Song"] = strawberry_django.field(filters=filters.SongFilter)
    reviews: List["Review"] = strawberry_django.field(filters=filters.ReviewFilter)
    outfits: List["Outfit"] = strawberry_django.field(filters=filters.OutfitFilter)


@strawberry_django.type(models.Song, fields="__all__", pagination=True)
class Song:
    alternative_versions: List["Song"] = strawberry_django.field(filters=filters.SongFilter)
    song_artists: List["SongArtist"] = strawberry_django.field(filters=filters.SongArtistFilter)
    project_songs: List["ProjectSong"] = strawberry_django.field(filters=filters.ProjectSongFilter)
    music_videos: List["MusicVideo"] = strawberry_django.field(filters=filters.MusicVideoFilter)
    reviews: List["Review"] = strawberry_django.field(filters=filters.ReviewFilter)


@strawberry_django.type(models.SongArtist, fields="__all__", pagination=True)
class SongArtist:
    song: "Song"
    artist: "Artist"


@strawberry_django.type(models.Project, fields="__all__", pagination=True)
class Project:
    covers: List["Cover"] = strawberry_django.field(filters=filters.CoverFilter)
    alternative_versions: List["Project"] = strawberry_django.field(filters=filters.ProjectFilter)
    project_songs: List["ProjectSong"] = strawberry_django.field(filters=filters.ProjectSongFilter)
    project_artists: List["ProjectArtist"] = strawberry_django.field(filters=filters.ProjectArtistFilter)
    reviews: List["Review"] = strawberry_django.field(filters=filters.ReviewFilter)


@strawberry_django.type(models.ProjectArtist, fields="__all__", pagination=True)
class ProjectArtist:
    project: "Project"
    artist: "Artist"


@strawberry_django.type(models.ProjectSong, fields="__all__", pagination=True)
class ProjectSong:
    project: "Project"
    song: "Song"


@strawberry_django.type(models.Podcast, fields="__all__", pagination=True)
class Podcast:
    hosts: List["Artist"] = strawberry_django.field(filters=filters.ArtistFilter)
    covers: List["Cover"] = strawberry_django.field(filters=filters.CoverFilter)
    reviews: List["Review"] = strawberry_django.field(filters=filters.ReviewFilter)


@strawberry_django.type(models.Outfit, fields="__all__", pagination=True)
class Outfit:
    artist: "Artist"
    music_videos: List["MusicVideo"] = strawberry_django.field(filters=filters.MusicVideoFilter)
    covers: List["Cover"] = strawberry_django.field(filters=filters.CoverFilter)
    matches: List["Outfit"] = strawberry_django.field(filters=filters.OutfitFilter)
    events: List["Event"] = strawberry_django.field(filters=filters.EventFilter)
    reviews: List["Review"] = strawberry_django.field(filters=filters.ReviewFilter)


@strawberry_django.type(models.Conversation, fields="__all__", pagination=True)
class Conversation:
    latest_message: Optional["Message"]
    latest_message_sender: Optional["User"]
    participants: List["User"] = strawberry_django.field(filters=filters.UserFilter)
    messages: List["Message"] = strawberry_django.field(filters=filters.MessageFilter)


@strawberry_django.type(models.Message, fields="__all__", pagination=True)
class Message:
    conversation: "Conversation"
    sender: Optional["User"]
    replying_to: Optional["Message"]
    liked_by: List["User"] = strawberry_django.field(filters=filters.UserFilter)


@strawberry_django.type(models.Profile, fields="__all__", pagination=True)
class Profile:
    user: "User"
    followers: List["Profile"] = strawberry_django.field(filters=filters.ProfileFilter)
    following: List["Profile"] = strawberry_django.field(filters=filters.ProfileFilter)


# The Unions still work correctly with these simplified types
Reviewable = strawberry.union(
    "Reviewable",
    (Event, Project, Song, MusicVideo, Podcast, Outfit, Cover),
)

Coverable = strawberry.union(
    "Coverable",
    (Project, Podcast),
)