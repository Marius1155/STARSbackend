# graphql/types.py

import strawberry
import strawberry_django
from STARS import models

@strawberry_django.type(models.Artist, fields="__all__")
class Artist:
    pass

@strawberry_django.type(models.EventSeries, fields="__all__")
class EventSeries:
    pass

@strawberry_django.type(models.Event, fields="__all__")
class Event:
    pass

@strawberry_django.type(models.User, fields=["id", "username", "email", "first_name", "last_name", "profile", "conversations", "reviews"])
class User:
    pass

@strawberry_django.type(models.Review, fields="__all__")
class Review:
    pass

@strawberry_django.type(models.SubReview, fields="__all__")
class SubReview:
    pass

@strawberry_django.type(models.Cover, fields="__all__")
class Cover:
    pass

@strawberry_django.type(models.MusicVideo, fields="__all__")
class MusicVideo:
    pass

@strawberry_django.type(models.Song, fields="__all__")
class Song:
    pass

@strawberry_django.type(models.SongArtist, fields="__all__")
class SongArtist:
    pass

@strawberry_django.type(models.Project, fields="__all__")
class Project:
    pass

@strawberry_django.type(models.ProjectArtist, fields="__all__")
class ProjectArtist:
    pass

@strawberry_django.type(models.ProjectSong, fields="__all__")
class ProjectSong:
    pass

@strawberry_django.type(models.Podcast, fields="__all__")
class Podcast:
    pass

@strawberry_django.type(models.Outfit, fields="__all__")
class Outfit:
    pass

@strawberry_django.type(models.Conversation, fields="__all__")
class Conversation:
    pass

@strawberry_django.type(models.Message, fields="__all__")
class Message:
    pass

@strawberry_django.type(models.Profile, fields="__all__")
class Profile:
    pass


# The Unions still need to be defined with their members
Reviewable = strawberry.union(
    "Reviewable",
    (Event, Project, Song, MusicVideo, Podcast, Outfit, Cover),
)

Coverable = strawberry.union(
    "Coverable",
    (Project, Podcast),
)