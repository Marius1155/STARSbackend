import strawberry
import strawberry_django
from strawberry_django.optimizer import DjangoOptimizerExtension
from strawberry import relay

from . import types, filters, mutations, subscriptions


@strawberry.type
class Query:
    artists: relay.Connection[types.Artist] = strawberry_django.connection(filters=filters.ArtistFilter)
    projects: relay.Connection[types.Project] = strawberry_django.connection(filters=filters.ProjectFilter)
    songs: relay.Connection[types.Song] = strawberry_django.connection(filters=filters.SongFilter)
    podcasts: relay.Connection[types.Podcast] = strawberry_django.connection(filters=filters.PodcastFilter)
    outfits: relay.Connection[types.Outfit] = strawberry_django.connection(filters=filters.OutfitFilter)
    comments: relay.Connection[types.Comment] = strawberry_django.connection(filters=filters.CommentFilter)
    reviews: relay.Connection[types.Review] = strawberry_django.connection(filters=filters.ReviewFilter)
    messages: relay.Connection[types.Message] = strawberry_django.connection(filters=filters.MessageFilter)
    conversations: relay.Connection[types.Conversation] = strawberry_django.connection(filters=filters.ConversationFilter)
    events: relay.Connection[types.Event] = strawberry_django.connection(filters=filters.EventFilter)
    event_series: relay.Connection[types.EventSeries] = strawberry_django.connection(filters=filters.EventSeriesFilter)
    music_videos: relay.Connection[types.MusicVideo] = strawberry_django.connection(filters=filters.MusicVideoFilter)
    users: relay.Connection[types.User] = strawberry_django.connection(filters=filters.UserFilter)

    # These are not paginated
    project_songs: list[types.ProjectSong] = strawberry_django.field(filters=filters.ProjectSongFilter)
    project_artists: list[types.ProjectArtist] = strawberry_django.field(filters=filters.ProjectArtistFilter)
    song_artists: list[types.SongArtist] = strawberry_django.field(filters=filters.SongArtistFilter)
    sub_reviews: list[types.SubReview] = strawberry_django.field(filters=filters.SubReviewFilter)
    profiles: list[types.Profile] = strawberry_django.field(filters=filters.ProfileFilter)
    covers: list[types.Cover] = strawberry_django.field(filters=filters.CoverFilter)


schema = strawberry.Schema(
    query=Query,
    mutation=mutations.Mutation,
    subscription=subscriptions.Subscription,
    extensions=[DjangoOptimizerExtension],
)