import strawberry
import strawberry_django
from strawberry_django.optimizer import DjangoOptimizerExtension
from strawberry_django.relay import DjangoCursorConnection

from . import types, filters, mutations, subscriptions


@strawberry.type
class Query:
    artists: DjangoCursorConnection[types.Artist] = strawberry_django.connection(filters=filters.ArtistFilter)
    projects: DjangoCursorConnection[types.Project] = strawberry_django.connection(filters=filters.ProjectFilter)
    songs: DjangoCursorConnection[types.Song] = strawberry_django.connection(filters=filters.SongFilter)
    podcasts: DjangoCursorConnection[types.Podcast] = strawberry_django.connection(filters=filters.PodcastFilter)
    outfits: DjangoCursorConnection[types.Outfit] = strawberry_django.connection(filters=filters.OutfitFilter)
    comments: DjangoCursorConnection[types.Comment] = strawberry_django.connection(filters=filters.CommentFilter)
    reviews: DjangoCursorConnection[types.Review] = strawberry_django.connection(filters=filters.ReviewFilter)
    messages: DjangoCursorConnection[types.Message] = strawberry_django.connection(filters=filters.MessageFilter)
    conversations: DjangoCursorConnection[types.Conversation] = strawberry_django.connection(filters=filters.ConversationFilter)
    events: DjangoCursorConnection[types.Event] = strawberry_django.connection(filters=filters.EventFilter)
    event_series: DjangoCursorConnection[types.EventSeries] = strawberry_django.connection(filters=filters.EventSeriesFilter)
    music_videos: DjangoCursorConnection[types.MusicVideo] = strawberry_django.connection(filters=filters.MusicVideoFilter)
    users: DjangoCursorConnection[types.User] = strawberry_django.connection(filters=filters.UserFilter)

    # These are not paginated
    project_songs: DjangoCursorConnection[types.ProjectSong] = strawberry_django.connection(filters=filters.ProjectSongFilter)
    project_artists: DjangoCursorConnection[types.ProjectArtist] = strawberry_django.connection(filters=filters.ProjectArtistFilter)
    song_artists: DjangoCursorConnection[types.SongArtist] = strawberry_django.connection(filters=filters.SongArtistFilter)
    sub_reviews: DjangoCursorConnection[types.SubReview] = strawberry_django.connection(filters=filters.SubReviewFilter)
    profiles: DjangoCursorConnection[types.Profile] = strawberry_django.connection(filters=filters.ProfileFilter)
    covers: DjangoCursorConnection[types.Cover] = strawberry_django.connection(filters=filters.CoverFilter)

schema = strawberry.Schema(
    query=Query,
    mutation=mutations.Mutation,
    subscription=subscriptions.Subscription,
    extensions=[DjangoOptimizerExtension],
)