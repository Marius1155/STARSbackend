# STARS/graphql/schema.py

import strawberry
import strawberry_django
from strawberry_django.optimizer import DjangoOptimizerExtension

# Import your type, filter, and mutation definitions
from . import types
from . import filters
from . import mutations

# --- Explicitly import all input types to ensure they are registered ---
from .mutations import (
    ArtistCreateInput,
    ArtistUpdateInput,
    EventSeriesCreateInput,
    EventSeriesUpdateInput,
    EventCreateInput,
    EventUpdateInput,
    ReviewCreateInput,
    ReviewUpdateInput,
    SubReviewCreateInput,
    SubReviewUpdateInput,
    MusicVideoCreateInput,
    MusicVideoUpdateInput,
    SongCreateInput,
    SongUpdateInput,
    ProjectCreateInput,
    ProjectUpdateInput,
    PodcastCreateInput,
    PodcastUpdateInput,
    OutfitCreateInput,
    OutfitUpdateInput,
    ProfileUpdateInput,
    SignupInput,  # <-- CORRECTED: Was UserCreateInput
    SongArtistCreateInput,
    ProjectArtistCreateInput,
    ProjectSongCreateInput,
)

@strawberry.type
class Query:
    artists: list[types.Artist] = strawberry_django.field(filters=filters.ArtistFilter)
    projects: list[types.Project] = strawberry_django.field(filters=filters.ProjectFilter)
    songs: list[types.Song] = strawberry_django.field(filters=filters.SongFilter)
    project_songs: list[types.ProjectSong] = strawberry_django.field(filters=filters.ProjectSongFilter)
    project_artists: list[types.ProjectArtist] = strawberry_django.field(filters=filters.ProjectArtistFilter)
    song_artists: list[types.SongArtist] = strawberry_django.field(filters=filters.SongArtistFilter)
    podcasts: list[types.Podcast] = strawberry_django.field(filters=filters.PodcastFilter)
    outfits: list[types.Outfit] = strawberry_django.field(filters=filters.OutfitFilter)
    reviews: list[types.Review] = strawberry_django.field(filters=filters.ReviewFilter)
    sub_reviews: list[types.SubReview] = strawberry_django.field(filters=filters.SubReviewFilter)
    profiles: list[types.Profile] = strawberry_django.field(filters=filters.ProfileFilter)
    messages: list[types.Message] = strawberry_django.field(filters=filters.MessageFilter)
    conversations: list[types.Conversation] = strawberry_django.field(filters=filters.ConversationFilter)
    events: list[types.Event] = strawberry_django.field(filters=filters.EventFilter)
    event_series: list[types.EventSeries] = strawberry_django.field(filters=filters.EventSeriesFilter)
    covers: list[types.Cover] = strawberry_django.field(filters=filters.CoverFilter)
    music_videos: list[types.MusicVideo] = strawberry_django.field(filters=filters.MusicVideoFilter)
    users: list[types.User] = strawberry_django.field(filters=filters.UserFilter)


# Pass the mutation class to the schema constructor
schema = strawberry.Schema(
    query=Query,
    mutation=mutations.Mutation,
    extensions=[
        DjangoOptimizerExtension,
    ]
)
