# STARS/graphql/schema.py

import strawberry
import strawberry_django
from strawberry_django.optimizer import DjangoOptimizerExtension

from . import types

@strawberry.type
class Query:
    artists: list[types.Artist] = strawberry_django.field()
    projects: list[types.Project] = strawberry_django.field()
    songs: list[types.Song] = strawberry_django.field()
    project_songs: list[types.ProjectSong] = strawberry_django.field()
    project_artists: list[types.ProjectArtist] = strawberry_django.field()
    song_artists: list[types.SongArtist] = strawberry_django.field()
    podcasts: list[types.Podcast] = strawberry_django.field()
    outfits: list[types.Outfit] = strawberry_django.field()
    reviews: list[types.Review] = strawberry_django.field()
    sub_reviews: list[types.SubReview] = strawberry_django.field()
    profiles: list[types.Profile] = strawberry_django.field()
    messages: list[types.Message] = strawberry_django.field()
    conversations: list[types.Conversation] = strawberry_django.field()
    events: list[types.Event] = strawberry_django.field()
    event_series: list[types.EventSeries] = strawberry_django.field()
    covers: list[types.Cover] = strawberry_django.field()
    music_videos: list[types.MusicVideo] = strawberry_django.field()
    users: list[types.User] = strawberry_django.field()

# We add the DjangoOptimizerExtension here. This is the crucial fix.
schema = strawberry.Schema(
    query=Query,
    extensions=[
        DjangoOptimizerExtension,
    ]
)