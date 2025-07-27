# graphql/types.py

import strawberry
import strawberry_django
from STARS import models

@strawberry_django.type(models.Artist)
class Artist:
    pass

@strawberry_django.type(models.EventSeries)
class EventSeries:
    pass

@strawberry_django.type(models.Event)
class Event:
    pass

@strawberry_django.type(models.User)
class User:
    pass

@strawberry_django.type(models.Review)
class Review:
    pass

@strawberry_django.type(models.SubReview)
class SubReview:
    pass

@strawberry_django.type(models.Cover)
class Cover:
    pass

@strawberry_django.type(models.MusicVideo)
class MusicVideo:
    pass

@strawberry_django.type(models.Song)
class Song:
    pass

@strawberry_django.type(models.SongArtist)
class SongArtist:
    pass

@strawberry_django.type(models.Project)
class Project:
    pass

@strawberry_django.type(models.ProjectArtist)
class ProjectArtist:
    pass

@strawberry_django.type(models.ProjectSong)
class ProjectSong:
    pass

@strawberry_django.type(models.Podcast)
class Podcast:
    pass

@strawberry_django.type(models.Outfit)
class Outfit:
    pass

@strawberry_django.type(models.Conversation)
class Conversation:
    pass

@strawberry_django.type(models.Message)
class Message:
    pass

@strawberry_django.type(models.Profile)
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