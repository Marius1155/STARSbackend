import strawberry
import strawberry_django
from strawberry import relay
from strawberry.types import Info
from strawberry_django.optimizer import DjangoOptimizerExtension

# Import your models and other GraphQL types
from . import types
from . import filters
from . import mutations
from STARS import models

# ... all your other imports ...

@strawberry.type
class Query:
    # This is our robust, manual resolver for the 'projects' field
    @strawberry.field
    def projects(self, info: Info, filters: filters.ProjectFilter | None = None) -> relay.Connection[types.Project]:
        """Manually resolves the projects connection."""
        queryset = models.Project.objects.all()

        if filters:
            # Convert the filter input into a dictionary and apply it
            filter_data = strawberry.asdict(filters)
            queryset = strawberry_django.filter(queryset, lookups=filter_data)

        return queryset

    # The rest of the queries still use the original helper for now.
    # If this fix works, we can apply it to the others if they fail.
    artists: relay.Connection[types.Artist] = strawberry_django.connection(filters=filters.ArtistFilter)
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

    # These fields are fine as they are
    project_songs: list[types.ProjectSong] = strawberry_django.field(filters=filters.ProjectSongFilter)
    project_artists: list[types.ProjectArtist] = strawberry_django.field(filters=filters.ProjectArtistFilter)
    song_artists: list[types.SongArtist] = strawberry_django.field(filters=filters.SongArtistFilter)
    sub_reviews: list[types.SubReview] = strawberry_django.field(filters=filters.SubReviewFilter)
    profiles: list[types.Profile] = strawberry_django.field(filters=filters.ProfileFilter)
    covers: list[types.Cover] = strawberry_django.field(filters=filters.CoverFilter)

    node: relay.Node = relay.node()


# Pass the mutation class to the schema constructor
schema = strawberry.Schema(
    query=Query,
    mutation=mutations.Mutation,
    extensions=[
        DjangoOptimizerExtension,
    ]
)