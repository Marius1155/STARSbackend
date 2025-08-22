import strawberry
import strawberry_django
from typing import Optional
from strawberry import relay

from STARS import models
from django.contrib.auth.models import User as DjangoUser

# Import your filters to use them in the fields
from . import filters


@strawberry_django.type(models.Artist, fields="__all__")
class Artist(strawberry.relay.Node):
    song_artists: relay.Connection["SongArtist"] = strawberry_django.connection(filters=filters.SongArtistFilter)
    project_artists: relay.Connection["ProjectArtist"] = strawberry_django.connection(filters=filters.ProjectArtistFilter)
    outfits: relay.Connection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter)
    podcasts: relay.Connection["Podcast"] = strawberry_django.connection(filters=filters.PodcastFilter)


@strawberry_django.type(models.EventSeries, fields="__all__")
class EventSeries(strawberry.relay.Node):
    events: relay.Connection["Event"] = strawberry_django.connection(filters=filters.EventFilter)


@strawberry_django.type(models.Event, fields="__all__")
class Event(strawberry.relay.Node):
    series: "EventSeries"
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)
    outfits: relay.Connection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter)


@strawberry_django.type(
    DjangoUser,
    fields=["id", "username", "email", "first_name", "is_staff", "is_superuser"]
)
class User(strawberry.relay.Node):
    profile: "Profile"
    conversations: relay.Connection["Conversation"] = strawberry_django.connection(filters=filters.ConversationFilter)
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)


@strawberry_django.type(models.Comment, fields="__all__")
class Comment(strawberry.relay.Node):
    review: "Review"
    user: "User"
    liked_by: relay.Connection["User"] = strawberry_django.connection(filters=filters.UserFilter)
    disliked_by: relay.Connection["User"] = strawberry_django.connection(filters=filters.UserFilter)


@strawberry_django.type(models.Review, fields="__all__")
class Review(strawberry.relay.Node):
    user: "User"
    content_object: "Reviewable"
    subreviews: relay.Connection["SubReview"] = strawberry_django.connection(filters=filters.SubReviewFilter)
    liked_by: relay.Connection["User"] = strawberry_django.connection(filters=filters.UserFilter)
    disliked_by: relay.Connection["User"] = strawberry_django.connection(filters=filters.UserFilter)


@strawberry_django.type(models.SubReview, fields="__all__")
class SubReview(strawberry.relay.Node):
    review: "Review"


@strawberry_django.type(models.Cover, fields="__all__")
class Cover(strawberry.relay.Node):
    content_object: "Coverable"
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)


@strawberry_django.type(models.MusicVideo, fields="__all__")
class MusicVideo(strawberry.relay.Node):
    songs: relay.Connection["Song"] = strawberry_django.connection(filters=filters.SongFilter)
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)
    outfits: relay.Connection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter)


@strawberry_django.type(models.Song, fields="__all__")
class Song(strawberry.relay.Node):
    alternative_versions: relay.Connection["Song"] = strawberry_django.connection(filters=filters.SongFilter)
    song_artists: relay.Connection["SongArtist"] = strawberry_django.connection(filters=filters.SongArtistFilter)
    project_songs: relay.Connection["ProjectSong"] = strawberry_django.connection(filters=filters.ProjectSongFilter)
    music_videos: relay.Connection["MusicVideo"] = strawberry_django.connection(filters=filters.MusicVideoFilter)
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)


@strawberry_django.type(models.SongArtist, fields="__all__")
class SongArtist(strawberry.relay.Node):
    song: "Song"
    artist: "Artist"


@strawberry_django.type(models.Project, fields="__all__")
class Project(strawberry.relay.Node):
    covers: relay.Connection["Cover"] = strawberry_django.connection(filters=filters.CoverFilter)
    alternative_versions: relay.Connection["Project"] = strawberry_django.connection(filters=filters.ProjectFilter)
    project_songs: relay.Connection["ProjectSong"] = strawberry_django.connection(filters=filters.ProjectSongFilter)
    project_artists: relay.Connection["ProjectArtist"] = strawberry_django.connection(filters=filters.ProjectArtistFilter)
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)


@strawberry_django.type(models.ProjectArtist, fields="__all__")
class ProjectArtist(strawberry.relay.Node):
    project: "Project"
    artist: "Artist"


@strawberry_django.type(models.ProjectSong, fields="__all__")
class ProjectSong(strawberry.relay.Node):
    project: "Project"
    song: "Song"


@strawberry_django.type(models.Podcast, fields="__all__")
class Podcast(strawberry.relay.Node):
    hosts: relay.Connection["Artist"] = strawberry_django.connection(filters=filters.ArtistFilter)
    covers: relay.Connection["Cover"] = strawberry_django.connection(filters=filters.CoverFilter)
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)


@strawberry_django.type(models.Outfit, fields="__all__")
class Outfit(strawberry.relay.Node):
    artist: "Artist"
    music_videos: relay.Connection["MusicVideo"] = strawberry_django.connection(filters=filters.MusicVideoFilter)
    covers: relay.Connection["Cover"] = strawberry_django.connection(filters=filters.CoverFilter)
    matches: relay.Connection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter)
    events: relay.Connection["Event"] = strawberry_django.connection(filters=filters.EventFilter)
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)


@strawberry_django.type(models.Conversation, fields="__all__")
class Conversation(strawberry.relay.Node):
    latest_message: Optional["Message"]
    latest_message_sender: Optional["User"]
    participants: relay.Connection["User"] = strawberry_django.connection(filters=filters.UserFilter)
    messages: relay.Connection["Message"] = strawberry_django.connection(filters=filters.MessageFilter)


@strawberry_django.type(models.Message, fields="__all__")
class Message(strawberry.relay.Node):
    conversation: "Conversation"
    sender: Optional["User"]
    replying_to: Optional["Message"]
    liked_by: relay.Connection["User"] = strawberry_django.connection(filters=filters.UserFilter)


@strawberry_django.type(models.Profile, fields="__all__")
class Profile(strawberry.relay.Node):
    user: "User"
    followers: relay.Connection["Profile"] = strawberry_django.connection(filters=filters.ProfileFilter)
    following: relay.Connection["Profile"] = strawberry_django.connection(filters=filters.ProfileFilter)


# The Unions still work correctly with these simplified types
Reviewable = strawberry.union(
    "Reviewable",
    (Event, Project, Song, MusicVideo, Podcast, Outfit, Cover),
)

Coverable = strawberry.union(
    "Coverable",
    (Project, Podcast),
)