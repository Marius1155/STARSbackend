# graphql/types.py

import strawberry
import strawberry_django
from STARS import models

@strawberry_django.type(models.Artist, fields="__all__")
class Artist:
    song_artists: list["SongArtist"]
    project_artists: list["ProjectArtist"]
    outfits: list["Outfit"]
    podcasts: list["Podcast"]

@strawberry_django.type(models.EventSeries, fields="__all__")
class EventSeries:
    events: list["Event"]

@strawberry_django.type(models.Event, fields="__all__")
class Event:
    reviews: list["Review"]
    outfits: list["Outfit"]

@strawberry_django.type(models.User, fields=["id", "username", "email", "first_name", "last_name", "profile"])
class User:
    conversations: list["Conversation"]
    reviews: list["Review"]

@strawberry_django.type(models.Review, fields="__all__")
class Review:
    content_object: "Reviewable"
    subreviews: list["SubReview"]

@strawberry_django.type(models.SubReview, fields="__all__")
class SubReview:
    pass

@strawberry_django.type(models.Cover, fields="__all__")
class Cover:
    content_object: "Coverable"
    reviews: list["Review"]

@strawberry_django.type(models.MusicVideo, fields="__all__")
class MusicVideo:
    songs: list["Song"]
    reviews: list["Review"]
    outfits: list["Outfit"]

@strawberry_django.type(models.Song, fields="__all__")
class Song:
    reviews: list["Review"]
    alternative_versions: list["Song"]
    song_artists: list["SongArtist"]
    project_songs: list["ProjectSong"]
    music_videos: list["MusicVideo"]

@strawberry_django.type(models.SongArtist, fields="__all__")
class SongArtist:
    pass

@strawberry_django.type(models.Project, fields="__all__")
class Project:
    covers: list["Cover"]
    reviews: list["Review"]
    alternative_versions: list["Project"]
    project_songs: list["ProjectSong"]
    project_artists: list["ProjectArtist"]

@strawberry_django.type(models.ProjectArtist, fields="__all__")
class ProjectArtist:
    pass

@strawberry_django.type(models.ProjectSong, fields="__all__")
class ProjectSong:
    pass

@strawberry_django.type(models.Podcast, fields="__all__")
class Podcast:
    hosts: list["Artist"]
    covers: list["Cover"]
    reviews: list["Review"]

@strawberry_django.type(models.Outfit, fields="__all__")
class Outfit:
    events: list["Event"]
    music_videos: list["MusicVideo"]
    covers: list["Cover"]
    reviews: list["Review"]
    matches: list["Outfit"]

@strawberry_django.type(models.Conversation, fields="__all__")
class Conversation:
    participants: list["User"]
    messages: list["Message"]

@strawberry_django.type(models.Message, fields="__all__")
class Message:
    liked_by: list["User"]

@strawberry_django.type(models.Profile, fields="__all__")
class Profile:
    followers: list["Profile"]
    following: list["Profile"]


# The Unions still need to be defined with their members
Reviewable = strawberry.union(
    "Reviewable",
    (Event, Project, Song, MusicVideo, Podcast, Outfit, Cover),
)

Coverable = strawberry.union(
    "Coverable",
    (Project, Podcast),
)