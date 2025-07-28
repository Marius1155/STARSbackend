# STARS/graphql/types.py

import strawberry
import strawberry_django
from strawberry import relay # <-- Make sure relay is imported
from STARS import models

# Import your filters to use them in the fields
from . import filters

# Any type used in a Connection must inherit from relay.Node
@strawberry_django.type(models.Artist, fields="__all__")
class Artist(relay.Node):
    id: relay.NodeID[int] # <-- ADD THIS LINE
    song_artists: list["SongArtist"] = strawberry_django.field(filters=filters.SongArtistFilter)
    project_artists: list["ProjectArtist"] = strawberry_django.field(filters=filters.ProjectArtistFilter)
    outfits: list["Outfit"] = strawberry_django.field(filters=filters.OutfitFilter)
    podcasts: list["Podcast"] = strawberry_django.field(filters=filters.PodcastFilter)

@strawberry_django.type(models.EventSeries, fields="__all__")
class EventSeries(relay.Node):
    id: relay.NodeID[int] # <-- ADD THIS LINE
    events: relay.Connection["Event"] = strawberry_django.connection(filters=filters.EventFilter)

@strawberry_django.type(models.Event, fields="__all__")
class Event(relay.Node):
    id: relay.NodeID[int] # <-- ADD THIS LINE
    series: "EventSeries"
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)
    outfits: relay.Connection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter)

@strawberry_django.type(models.User) # Note: User does not need to be a Node unless you query it directly as a paginated field
class User:
    id: strawberry.ID # Use standard ID for non-node types
    username: strawberry.auto
    email: strawberry.auto
    first_name: strawberry.auto
    last_name: strawberry.auto
    profile: "Profile"
    conversations: relay.Connection["Conversation"] = strawberry_django.connection(filters=filters.ConversationFilter)
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)

@strawberry_django.type(models.Review, fields="__all__")
class Review(relay.Node):
    id: relay.NodeID[int] # <-- ADD THIS LINE
    user: "User"
    content_object: "Reviewable"
    subreviews: list["SubReview"] = strawberry_django.field(filters=filters.SubReviewFilter)

@strawberry_django.type(models.SubReview, fields="__all__")
class SubReview:
    review: "Review"

@strawberry_django.type(models.Cover, fields="__all__")
class Cover:
    content_object: "Coverable"
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)

@strawberry_django.type(models.MusicVideo, fields="__all__")
class MusicVideo(relay.Node):
    id: relay.NodeID[int] # <-- ADD THIS LINE
    songs: list["Song"] = strawberry_django.field(filters=filters.SongFilter)
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)
    outfits: relay.Connection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter)

@strawberry_django.type(models.Song, fields="__all__")
class Song(relay.Node):
    id: relay.NodeID[int] # <-- ADD THIS LINE
    alternative_versions: list["Song"] = strawberry_django.field(filters=filters.SongFilter)
    song_artists: list["SongArtist"] = strawberry_django.field(filters=filters.SongArtistFilter)
    project_songs: list["ProjectSong"] = strawberry_django.field(filters=filters.ProjectSongFilter)
    music_videos: list["MusicVideo"] = strawberry_django.field(filters=filters.MusicVideoFilter)
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)


@strawberry_django.type(models.SongArtist, fields="__all__")
class SongArtist:
    song: "Song"
    artist: "Artist"

@strawberry_django.type(models.Project, fields="__all__")
class Project(relay.Node):
    id: relay.NodeID[int] # <-- ADD THIS LINE
    covers: list["Cover"] = strawberry_django.field(filters=filters.CoverFilter)
    alternative_versions: list["Project"] = strawberry_django.field(filters=filters.ProjectFilter)
    project_songs: list["ProjectSong"] = strawberry_django.field(filters=filters.ProjectSongFilter)
    project_artists: list["ProjectArtist"] = strawberry_django.field(filters=filters.ProjectArtistFilter)
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)


@strawberry_django.type(models.ProjectArtist, fields="__all__")
class ProjectArtist:
    project: "Project"
    artist: "Artist"

@strawberry_django.type(models.ProjectSong, fields="__all__")
class ProjectSong:
    project: "Project"
    song: "Song"

@strawberry_django.type(models.Podcast, fields="__all__")
class Podcast(relay.Node):
    id: relay.NodeID[int] # <-- ADD THIS LINE
    hosts: list["Artist"] = strawberry_django.field(filters=filters.ArtistFilter)
    covers: list["Cover"] = strawberry_django.field(filters=filters.CoverFilter)
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)

@strawberry_django.type(models.Outfit, fields="__all__")
class Outfit(relay.Node):
    id: relay.NodeID[int] # <-- ADD THIS LINE
    artist: "Artist"
    music_videos: list["MusicVideo"] = strawberry_django.field(filters=filters.MusicVideoFilter)
    covers: list["Cover"] = strawberry_django.field(filters=filters.CoverFilter)
    matches: list["Outfit"] = strawberry_django.field(filters=filters.OutfitFilter)
    events: relay.Connection["Event"] = strawberry_django.connection(filters=filters.EventFilter)
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)


@strawberry_django.type(models.Conversation, fields="__all__")
class Conversation(relay.Node):
    id: relay.NodeID[int] # <-- ADD THIS LINE
    latest_message: "Message"
    latest_message_sender: "User"
    participants: list["User"] = strawberry_django.field(filters=filters.UserFilter)
    messages: relay.Connection["Message"] = strawberry_django.connection(filters=filters.MessageFilter)

@strawberry_django.type(models.Message, fields="__all__")
class Message(relay.Node):
    id: relay.NodeID[int] # <-- ADD THIS LINE
    conversation: "Conversation"
    sender: "User"
    replying_to: "Message"
    liked_by: list["User"] = strawberry_django.field(filters=filters.UserFilter)

@strawberry_django.type(models.Profile, fields="__all__")
class Profile:
    user: "User"
    followers: list["Profile"] = strawberry_django.field(filters=filters.ProfileFilter)
    following: list["Profile"] = strawberry_django.field(filters=filters.ProfileFilter)


# The Unions still need to be defined with their members
Reviewable = strawberry.union(
    "Reviewable",
    (Event, Project, Song, MusicVideo, Podcast, Outfit, Cover),
)

Coverable = strawberry.union(
    "Coverable",
    (Project, Podcast),
)
