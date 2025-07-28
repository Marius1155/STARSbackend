# STARS/graphql/schema.py

import strawberry
import strawberry_django
from strawberry import relay # <-- Make sure relay is imported
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
    SignupInput,
    SongArtistCreateInput,
    ProjectArtistCreateInput,
    ProjectSongCreateInput,
)

@strawberry.type
class Query:
    # Convert list fields to paginated connections using the correct path
    artists: relay.Connection[types.Artist] = strawberry_django.connection(filters=filters.ArtistFilter)
    projects: relay.Connection[types.Project] = strawberry_django.connection(filters=filters.ProjectFilter)
    songs: relay.Connection[types.Song] = strawberry_django.connection(filters=filters.SongFilter)
    podcasts: relay.Connection[types.Podcast] = strawberry_django.connection(filters=filters.PodcastFilter)
    outfits: relay.Connection[types.Outfit] = strawberry_django.connection(filters=filters.OutfitFilter)
    reviews: relay.Connection[types.Review] = strawberry_django.connection(filters=filters.ReviewFilter)
    messages: relay.Connection[types.Message] = strawberry_django.connection(filters=filters.MessageFilter)
    conversations: relay.Connection[types.Conversation] = strawberry_django.connection(filters=filters.ConversationFilter)
    events: relay.Connection[types.Event] = strawberry_django.connection(filters=filters.EventFilter)
    event_series: relay.Connection[types.EventSeries] = strawberry_django.connection(filters=filters.EventSeriesFilter)
    music_videos: relay.Connection[types.MusicVideo] = strawberry_django.connection(filters=filters.MusicVideoFilter)
    users: relay.Connection[types.User] = strawberry_django.connection(filters=filters.UserFilter)

    # These fields are less likely to need top-level pagination, so we leave them as lists
    project_songs: list[types.ProjectSong] = strawberry_django.field(filters=filters.ProjectSongFilter)
    project_artists: list[types.ProjectArtist] = strawberry_django.field(filters=filters.ProjectArtistFilter)
    song_artists: list[types.SongArtist] = strawberry_django.field(filters=filters.SongArtistFilter)
    sub_reviews: list[types.SubReview] = strawberry_django.field(filters=filters.SubReviewFilter)
    profiles: list[types.Profile] = strawberry_django.field(filters=filters.ProfileFilter)
    covers: list[types.Cover] = strawberry_django.field(filters=filters.CoverFilter)


# Pass the mutation class to the schema constructor
schema = strawberry.Schema(
    query=Query,
    mutation=mutations.Mutation,
    extensions=[
        DjangoOptimizerExtension,
    ]
)
