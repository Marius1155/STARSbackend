# graphql/schema.py

import strawberry
from . import types

# NO optimizer import needed here

@strawberry.type
class Query:
    artists: list[types.Artist] = strawberry.django.field()
    projects: list[types.Project] = strawberry.django.field()
    songs: list[types.Song] = strawberry.django.field()
    project_songs: list[types.ProjectSong] = strawberry.django.field()
    project_artists: list[types.ProjectArtist] = strawberry.django.field()
    song_artists: list[types.SongArtist] = strawberry.django.field()
    podcasts: list[types.Podcast] = strawberry.django.field()
    outfits: list[types.Outfit] = strawberry.django.field()
    reviews: list[types.Review] = strawberry.django.field()
    sub_reviews: list[types.SubReview] = strawberry.django.field()
    profiles: list[types.Profile] = strawberry.django.field()
    messages: list[types.Message] = strawberry.django.field()
    conversations: list[types.Conversation] = strawberry.django.field()
    events: list[types.Event] = strawberry.django.field()
    event_series: list[types.EventSeries] = strawberry.django.field()
    covers: list[types.Cover] = strawberry.django.field()
    music_videos: list[types.MusicVideo] = strawberry.django.field()
    users: list[types.User] = strawberry.django.field()

schema = strawberry.Schema(
    query=Query,
    # The extensions list is no longer needed for the optimizer
)