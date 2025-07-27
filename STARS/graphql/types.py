# STARS/graphql/types.py

import strawberry
import strawberry_django
from STARS import models

# Import your filters to use them in the fields
from . import filters

@strawberry_django.type(models.Artist, fields="__all__")
class Artist:
    # Explicitly define all relationship fields
    song_artists: list["SongArtist"] = strawberry_django.field(filters=filters.SongArtistFilter)
    project_artists: list["ProjectArtist"] = strawberry_django.field(filters=filters.ProjectArtistFilter)
    outfits: list["Outfit"] = strawberry_django.field(filters=filters.OutfitFilter)
    podcasts: list["Podcast"] = strawberry_django.field(filters=filters.PodcastFilter)

@strawberry_django.type(models.EventSeries, fields="__all__")
class EventSeries:
    events: list["Event"] = strawberry_django.field(filters=filters.EventFilter)

@strawberry_django.type(models.Event, fields="__all__")
class Event:
    series: "EventSeries"
    reviews: list["Review"] = strawberry_django.field(filters=filters.ReviewFilter)
    outfits: list["Outfit"] = strawberry_django.field(filters=filters.OutfitFilter)

@strawberry_django.type(models.User, fields=["id", "username", "email", "first_name", "last_name"])
class User:
    profile: "Profile"
    conversations: list["Conversation"] = strawberry_django.field(filters=filters.ConversationFilter)
    reviews: list["Review"] = strawberry_django.field(filters=filters.ReviewFilter)

@strawberry_django.type(models.Review, fields="__all__")
class Review:
    user: "User"
    content_object: "Reviewable"
    subreviews: list["SubReview"] = strawberry_django.field(filters=filters.SubReviewFilter)

@strawberry_django.type(models.SubReview, fields="__all__")
class SubReview:
    review: "Review"

@strawberry_django.type(models.Cover, fields="__all__")
class Cover:
    content_object: "Coverable"
    reviews: list["Review"] = strawberry_django.field(filters=filters.ReviewFilter)

@strawberry_django.type(models.MusicVideo, fields="__all__")
class MusicVideo:
    songs: list["Song"] = strawberry_django.field(filters=filters.SongFilter)
    reviews: list["Review"] = strawberry_django.field(filters=filters.ReviewFilter)
    outfits: list["Outfit"] = strawberry_django.field(filters=filters.OutfitFilter)

@strawberry_django.type(models.Song, fields="__all__")
class Song:
    reviews: list["Review"] = strawberry_django.field(filters=filters.ReviewFilter)
    alternative_versions: list["Song"] = strawberry_django.field(filters=filters.SongFilter)
    song_artists: list["SongArtist"] = strawberry_django.field(filters=filters.SongArtistFilter)
    project_songs: list["ProjectSong"] = strawberry_django.field(filters=filters.ProjectSongFilter)
    music_videos: list["MusicVideo"] = strawberry_django.field(filters=filters.MusicVideoFilter)

@strawberry_django.type(models.SongArtist, fields="__all__")
class SongArtist:
    song: "Song"
    artist: "Artist"

@strawberry_django.type(models.Project, fields="__all__")
class Project:
    covers: list["Cover"] = strawberry_django.field(filters=filters.CoverFilter)
    reviews: list["Review"] = strawberry_django.field(filters=filters.ReviewFilter)
    alternative_versions: list["Project"] = strawberry_django.field(filters=filters.ProjectFilter)
    project_songs: list["ProjectSong"] = strawberry_django.field(filters=filters.ProjectSongFilter)
    project_artists: list["ProjectArtist"] = strawberry_django.field(filters=filters.ProjectArtistFilter)

@strawberry_django.type(models.ProjectArtist, fields="__all__")
class ProjectArtist:
    project: "Project"
    artist: "Artist"

@strawberry_django.type(models.ProjectSong, fields="__all__")
class ProjectSong:
    project: "Project"
    song: "Song"

@strawberry_django.type(models.Podcast, fields="__all__")
class Podcast:
    hosts: list["Artist"] = strawberry_django.field(filters=filters.ArtistFilter)
    covers: list["Cover"] = strawberry_django.field(filters=filters.CoverFilter)
    reviews: list["Review"] = strawberry_django.field(filters=filters.ReviewFilter)

@strawberry_django.type(models.Outfit, fields="__all__")
class Outfit:
    artist: "Artist"
    events: list["Event"] = strawberry_django.field(filters=filters.EventFilter)
    music_videos: list["MusicVideo"] = strawberry_django.field(filters=filters.MusicVideoFilter)
    covers: list["Cover"] = strawberry_django.field(filters=filters.CoverFilter)
    reviews: list["Review"] = strawberry_django.field(filters=filters.ReviewFilter)
    matches: list["Outfit"] = strawberry_django.field(filters=filters.OutfitFilter)

@strawberry_django.type(models.Conversation, fields="__all__")
class Conversation:
    latest_message: "Message"
    latest_message_sender: "User"
    participants: list["User"] = strawberry_django.field(filters=filters.UserFilter)
    messages: list["Message"] = strawberry_django.field(filters=filters.MessageFilter)

@strawberry_django.type(models.Message, fields="__all__")
class Message:
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
