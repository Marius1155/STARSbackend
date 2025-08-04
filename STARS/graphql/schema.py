import strawberry
import strawberry_django
from strawberry_django.optimizer import DjangoOptimizerExtension
from strawberry_django.pagination import OffsetPaginated

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
    # All list fields are now wrapped in OffsetPaginated and include their respective filters
    artists: OffsetPaginated[types.Artist] = strawberry_django.field(pagination=True, filters=filters.ArtistFilter)
    allProjects: OffsetPaginated[types.Project] = strawberry_django.field(pagination=True, filters=filters.ProjectFilter)
    songs: OffsetPaginated[types.Song] = strawberry_django.field(pagination=True, filters=filters.SongFilter)
    podcasts: OffsetPaginated[types.Podcast] = strawberry_django.field(pagination=True, filters=filters.PodcastFilter)
    outfits: OffsetPaginated[types.Outfit] = strawberry_django.field(pagination=True, filters=filters.OutfitFilter)
    reviews: OffsetPaginated[types.Review] = strawberry_django.field(pagination=True, filters=filters.ReviewFilter)
    messages: OffsetPaginated[types.Message] = strawberry_django.field(pagination=True, filters=filters.MessageFilter)
    conversations: OffsetPaginated[types.Conversation] = strawberry_django.field(pagination=True, filters=filters.ConversationFilter)
    events: OffsetPaginated[types.Event] = strawberry_django.field(pagination=True, filters=filters.EventFilter)
    event_series: OffsetPaginated[types.EventSeries] = strawberry_django.field(pagination=True, filters=filters.EventSeriesFilter)
    music_videos: OffsetPaginated[types.MusicVideo] = strawberry_django.field(pagination=True, filters=filters.MusicVideoFilter)
    users: OffsetPaginated[types.User] = strawberry_django.field(pagination=True, filters=filters.UserFilter)

    # These fields are simple lists and do not need pagination
    project_songs: list[types.ProjectSong] = strawberry_django.field(filters=filters.ProjectSongFilter)
    project_artists: list[types.ProjectArtist] = strawberry_django.field(filters=filters.ProjectArtistFilter)
    song_artists: list[types.SongArtist] = strawberry_django.field(filters=filters.SongArtistFilter)
    sub_reviews: list[types.SubReview] = strawberry_django.field(filters=filters.SubReviewFilter)
    profiles: list[types.Profile] = strawberry_django.field(filters=filters.ProfileFilter)
    covers: list[types.Cover] = strawberry_django.field(filters=filters.CoverFilter)


schema = strawberry.Schema(
    query=Query,
    mutation=mutations.Mutation,
    extensions=[
        DjangoOptimizerExtension,
    ]
)