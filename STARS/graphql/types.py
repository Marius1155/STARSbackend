import strawberry
import strawberry_django
from strawberry.types import Info
from typing import Optional, Iterable, Any, List
from django.db.models import QuerySet
from strawberry_django.relay import DjangoCursorConnection
from STARS import models
from django.contrib.auth.models import User as DjangoUser
from asgiref.sync import sync_to_async
from strawberry import relay
from STARS import models
from STARS.models import PodcastGenre

# Import your filters to use them in the fields
from . import filters, orders

@strawberry.type
class MusicSearchResponse:
    artists: List["Artist"]
    projects: List["Project"]
    songs: List["Song"]
    music_videos: List["MusicVideo"]
    performance_videos: List["PerformanceVideo"]

@strawberry_django.type(models.MusicGenre, fields="__all__")
class MusicGenre(strawberry.relay.Node):
    projects: DjangoCursorConnection["Project"] = strawberry_django.connection(filters=filters.ProjectFilter, order=orders.ProjectOrder)
    songs: DjangoCursorConnection["Song"] = strawberry_django.connection(filters=filters.SongFilter, order=orders.SongOrder)
    artists: DjangoCursorConnection["Artist"] = strawberry_django.connection(filters=filters.ArtistFilter, order=orders.ArtistOrder)


@strawberry_django.type(models.PodcastGenre, fields="__all__")
class PodcastGenre(strawberry.relay.Node):
    podcasts: DjangoCursorConnection["Podcast"] = strawberry_django.connection(filters=filters.PodcastFilter, order=orders.PodcastOrder)


@strawberry_django.type(models.Artist, fields="__all__")
class Artist(strawberry.relay.Node):
    # Change DjangoCursorConnection to relay.ListConnection to match your Project type
    song_artists: relay.ListConnection["SongArtist"] = strawberry_django.connection(filters=filters.SongArtistFilter, order=orders.SongArtistOrder)
    project_artists: relay.ListConnection["ProjectArtist"] = strawberry_django.connection(filters=filters.ProjectArtistFilter, order=orders.ProjectArtistOrder)
    outfits: relay.ListConnection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter, order=orders.OutfitOrder)
    genres: relay.ListConnection["MusicGenre"] = strawberry_django.connection(filters=filters.MusicGenreFilter, order=orders.MusicGenreOrder)
    performance_videos: relay.ListConnection["PerformanceVideo"] = strawberry_django.connection(filters=filters.PerformanceVideoFilter, order=orders.PerformanceVideoOrder)

    # Add these async accessors to ensure safe DB access if needed by custom resolvers
    # or simply to match your Project pattern.
    @sync_to_async
    def get_song_artists(self) -> List[models.SongArtist]:
        return self.song_artists.all()

    @sync_to_async
    def get_project_artists(self) -> List[models.ProjectArtist]:
        return self.project_artists.all()

    @sync_to_async
    def get_outfits(self) -> List[models.Outfit]:
        return self.outfits.all()

    @sync_to_async
    def get_genres(self) -> List[models.MusicGenre]:
        return self.genres.all()

    @sync_to_async
    def get_performance_videos(self) -> List[models.PerformanceVideo]:
        return self.performance_videos.all()


@strawberry_django.type(models.EventSeries, fields="__all__")
class EventSeries(strawberry.relay.Node):
    events: DjangoCursorConnection["Event"] = strawberry_django.connection(filters=filters.EventFilter, order=orders.EventOrder)


@strawberry_django.type(models.Event, fields="__all__")
class Event(strawberry.relay.Node):
    reviews: DjangoCursorConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)
    outfits: DjangoCursorConnection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter, order=orders.OutfitOrder)
    performance_videos: DjangoCursorConnection["PerformanceVideo"] = strawberry_django.connection(filters=filters.PerformanceVideoFilter, order=orders.PerformanceVideoOrder)
    series: Optional["EventSeries"]


@strawberry_django.type(
    DjangoUser,
    fields=["id", "username", "email", "first_name", "is_staff", "is_superuser"]
)
class User(strawberry.relay.Node):
    profile: "Profile"
    conversations: DjangoCursorConnection["Conversation"] = strawberry_django.connection(filters=filters.ConversationFilter, order=orders.ConversationOrder)
    seen_conversations: DjangoCursorConnection["Conversation"] = strawberry_django.connection(filters=filters.ConversationFilter, order=orders.ConversationOrder)
    reviews: DjangoCursorConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)


@strawberry_django.type(models.Comment, fields="__all__")
class Comment(strawberry.relay.Node):
    review: "Review"
    user: "User"
    replying_to: "Comment"
    replies: DjangoCursorConnection["Comment"] = strawberry_django.connection(filters=filters.CommentFilter, order=orders.CommentOrder)
    liked_by: DjangoCursorConnection["User"] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)
    disliked_by: DjangoCursorConnection["User"] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)

    @strawberry.field
    async def liked_by_current_user(self, info: Info) -> bool:
        def check():
            user = info.context.request.user
            if user.is_anonymous:
                return False
            return self.liked_by.filter(pk=user.pk).exists()

        return await sync_to_async(check)()

    @strawberry.field
    async def disliked_by_current_user(self, info: Info) -> bool:
        def check():
            user = info.context.request.user
            if user.is_anonymous:
                return False
            return self.disliked_by.filter(pk=user.pk).exists()

        return await sync_to_async(check)()


@strawberry_django.type(models.Review, fields="__all__")
class Review(strawberry.relay.Node):
    user: "User"
    content_object: "Reviewable"
    subreviews: DjangoCursorConnection["SubReview"] = strawberry_django.connection(filters=filters.SubReviewFilter, order=orders.SubReviewOrder)
    comments: DjangoCursorConnection["Comment"] = strawberry_django.connection(filters=filters.CommentFilter, order=orders.CommentOrder)
    liked_by: DjangoCursorConnection["User"] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)
    disliked_by: DjangoCursorConnection["User"] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)

    @strawberry.field
    async def liked_by_current_user(self, info: Info) -> bool:
        def check():
            user = info.context.request.user
            if user.is_anonymous:
                return False
            return self.liked_by.filter(pk=user.pk).exists()

        return await sync_to_async(check)()

    @strawberry.field
    async def disliked_by_current_user(self, info: Info) -> bool:
        def check():
            user = info.context.request.user
            if user.is_anonymous:
                return False
            return self.disliked_by.filter(pk=user.pk).exists()

        return await sync_to_async(check)()

    @strawberry.field
    async def is_rereview(self) -> bool:
        """True if this user has older reviews for the same object."""

        def check():
            return models.Review.objects.filter(
                user=self.user,
                content_type=self.content_type,
                object_id=self.object_id,
                date_created__lt=self.date_created  # strictly older reviews
            ).exists()

        return await sync_to_async(check)()


@strawberry_django.type(models.SubReview, fields="__all__")
class SubReview(strawberry.relay.Node):
    review: "Review"


@strawberry_django.type(models.Cover, fields="__all__")
class Cover(strawberry.relay.Node):
    content_object: "Coverable"
    reviews: DjangoCursorConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)


@strawberry_django.type(models.MusicVideo, fields="__all__")
class MusicVideo(strawberry.relay.Node):
    songs: DjangoCursorConnection["Song"] = strawberry_django.connection(filters=filters.SongFilter, order=orders.SongOrder)
    reviews: DjangoCursorConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)
    outfits: DjangoCursorConnection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter, order=orders.OutfitOrder)


@strawberry_django.type(models.PerformanceVideo, fields="__all__")
class PerformanceVideo(strawberry.relay.Node):
    event: Optional["Event"]
    artists: DjangoCursorConnection["Artist"] = strawberry_django.connection(filters=filters.ArtistFilter, order=orders.ArtistOrder)
    songs: DjangoCursorConnection["Song"] = strawberry_django.connection(filters=filters.SongFilter, order=orders.SongOrder)
    reviews: DjangoCursorConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)
    outfits: DjangoCursorConnection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter, order=orders.OutfitOrder)


@strawberry_django.type(models.Song, fields="__all__")
class Song(strawberry.relay.Node):
    alternative_versions: relay.ListConnection["Song"] = strawberry_django.connection(filters=filters.SongFilter, order=orders.SongOrder)
    song_artists: relay.ListConnection["SongArtist"] = strawberry_django.connection(filters=filters.SongArtistFilter, order=orders.SongArtistOrder)
    project_songs: relay.ListConnection["ProjectSong"] = strawberry_django.connection(filters=filters.ProjectSongFilter, order=orders.ProjectSongOrder)
    music_videos: relay.ListConnection["MusicVideo"] = strawberry_django.connection(filters=filters.MusicVideoFilter, order=orders.MusicVideoOrder)
    performance_videos: relay.ListConnection["PerformanceVideo"] = strawberry_django.connection(filters=filters.PerformanceVideoFilter, order=orders.PerformanceVideoOrder)
    reviews: relay.ListConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)
    genres: relay.ListConnection["MusicGenre"] = strawberry_django.connection(filters=filters.MusicGenreFilter, order=orders.MusicGenreOrder)

    @sync_to_async
    def get_alternative_versions(self) -> relay.ListConnection["Song"]:
        return self.alternative_versions.all()

    @sync_to_async
    def get_song_artists(self) -> relay.ListConnection["SongArtist"]:
        return self.song_artists.all()

    @sync_to_async
    def get_project_songs(self) -> relay.ListConnection["ProjectSong"]:
        return self.project_songs.all()

    @sync_to_async
    def get_music_videos(self) -> relay.ListConnection["MusicVideo"]:
        return self.music_videos.all()

    @sync_to_async
    def get_performance_videos(self) -> relay.ListConnection["PerformanceVideo"]:
        return self.performance_videos.all()

    @sync_to_async
    def get_reviews(self) -> List[models.Review]:
        return self.reviews.all()

    @sync_to_async
    def get_genres(self) -> List[models.MusicGenre]:
        return self.genres.all()


@strawberry_django.type(models.SongArtist, fields="__all__")
class SongArtist(strawberry.relay.Node):
    song: "Song"
    artist: "Artist"


@strawberry_django.type(models.Project, fields="__all__")
class Project(relay.Node):
    covers: relay.ListConnection["Cover"] = strawberry_django.connection(filters=filters.CoverFilter, order=orders.CoverOrder)
    project_songs: relay.ListConnection["ProjectSong"] = strawberry_django.connection(filters=filters.ProjectSongFilter, order=orders.ProjectSongOrder)
    project_artists: relay.ListConnection["ProjectArtist"] = strawberry_django.connection(filters=filters.ProjectArtistFilter, order=orders.ProjectArtistOrder)
    reviews: relay.ListConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)
    alternative_versions: relay.ListConnection["Project"] = strawberry_django.connection(filters=filters.ProjectFilter, order=orders.ProjectOrder)
    genres: relay.ListConnection["MusicGenre"] = strawberry_django.connection(filters=filters.MusicGenreFilter, order=orders.MusicGenreOrder)

    @sync_to_async
    def get_covers(self) -> List[models.Cover]:
        return self.covers.all()

    @sync_to_async
    def get_project_songs(self) -> List[models.ProjectSong]:
        return self.project_songs.all()

    @sync_to_async
    def get_project_artists(self) -> List[models.ProjectArtist]:
        return self.project_artists.all()

    @sync_to_async
    def get_reviews(self) -> List[models.Review]:
        return self.reviews.all()

    @sync_to_async
    def get_alternative_versions(self) -> List[models.Project]:
        return self.alternative_versions.all()

    @sync_to_async
    def get_genres(self) -> List[models.MusicGenre]:
        return self.genres.all()


@strawberry_django.type(models.ProjectArtist, fields="__all__")
class ProjectArtist(strawberry.relay.Node):
    project: "Project"
    artist: "Artist"


@strawberry_django.type(models.ProjectSong, fields="__all__")
class ProjectSong(strawberry.relay.Node):
    project: "Project"
    song: "Song"


@strawberry_django.type(models.Podcast, fields="__all__")
class Podcast(strawberry.relay.Node):

    @strawberry.field
    async def covers(
            self,
            info: Info,
            first: Optional[int] = None,
            after: Optional[str] = None,
            before: Optional[str] = None,
            last: Optional[int] = None,
            filters: Optional[filters.CoverFilter] = None,
            order: Optional[orders.CoverOrder] = None,
    ) -> DjangoCursorConnection["Cover"]:
        """Async-wrapped cursor connection for podcast covers."""
        # Capture the filter/order values before the inner function
        filter_arg = filters
        order_arg = order

        def resolve_connection():
            from strawberry_django.relay import resolve_connection
            return resolve_connection(
                info=info,
                nodes=self.covers.all(),
                filters=filter_arg,  # Use the captured value
                order=order_arg,  # Use the captured value
                first=first,
                after=after,
                before=before,
                last=last,
            )

        return await sync_to_async(resolve_connection)()

    @strawberry.field
    async def reviews(
            self,
            info: Info,
            first: Optional[int] = None,
            after: Optional[str] = None,
            before: Optional[str] = None,
            last: Optional[int] = None,
            filters: Optional[filters.ReviewFilter] = None,
            order: Optional[orders.ReviewOrder] = None,
    ) -> DjangoCursorConnection["Review"]:
        """Async-wrapped cursor connection for podcast reviews."""
        filter_arg = filters
        order_arg = order

        def resolve_connection():
            from strawberry_django.relay import resolve_connection
            return resolve_connection(
                info=info,
                nodes=self.reviews.all(),
                filters=filter_arg,
                order=order_arg,
                first=first,
                after=after,
                before=before,
                last=last,
            )

        return await sync_to_async(resolve_connection)()

    @strawberry.field
    async def genres(
            self,
            info: Info,
            first: Optional[int] = None,
            after: Optional[str] = None,
            before: Optional[str] = None,
            last: Optional[int] = None,
            filters: Optional[filters.PodcastGenreFilter] = None,
            order: Optional[orders.PodcastGenreOrder] = None,
    ) -> DjangoCursorConnection["PodcastGenre"]:
        """Async-wrapped cursor connection for podcast genres."""
        filter_arg = filters
        order_arg = order

        def resolve_connection():
            from strawberry_django.relay import resolve_connection
            return resolve_connection(
                info=info,
                nodes=self.genres.all(),
                filters=filter_arg,
                order=order_arg,
                first=first,
                after=after,
                before=before,
                last=last,
            )

        return await sync_to_async(resolve_connection)()

@strawberry_django.type(models.Outfit, fields="__all__")
class Outfit(strawberry.relay.Node):
    artist: "Artist"
    music_videos: DjangoCursorConnection["MusicVideo"] = strawberry_django.connection(filters=filters.MusicVideoFilter, order=orders.MusicVideoOrder)
    covers: DjangoCursorConnection["Cover"] = strawberry_django.connection(filters=filters.CoverFilter, order=orders.CoverOrder)
    matches: DjangoCursorConnection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter, order=orders.OutfitOrder)
    events: DjangoCursorConnection["Event"] = strawberry_django.connection(filters=filters.EventFilter, order=orders.EventOrder)
    reviews: DjangoCursorConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)


@strawberry_django.type(models.Conversation, fields="__all__")
class Conversation(strawberry.relay.Node):
    latest_message: Optional["Message"]
    latest_message_sender: Optional["User"]
    participants: DjangoCursorConnection["User"] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)
    messages: DjangoCursorConnection["Message"] = strawberry_django.connection(filters=filters.MessageFilter, order=orders.MessageOrder)
    seen_by: DjangoCursorConnection["User"] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)


@strawberry_django.type(models.Message, fields="__all__")
class Message(strawberry.relay.Node):
    conversation: "Conversation"
    sender: Optional["User"]
    replying_to: Optional["Message"]
    liked_by: DjangoCursorConnection["User"] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)


@strawberry_django.type(models.Profile, fields="__all__")
class Profile(strawberry.relay.Node):
    user: "User"
    followers: DjangoCursorConnection["Profile"] = strawberry_django.connection(filters=filters.ProfileFilter, order=orders.ProfileOrder)
    following: DjangoCursorConnection["Profile"] = strawberry_django.connection(filters=filters.ProfileFilter, order=orders.ProfileOrder)


@strawberry_django.type(models.SearchHistory, fields="__all__")
class SearchHistory(strawberry.relay.Node):
    user: "User"


Reviewable = strawberry.union(
    "Reviewable",
    (Event, Project, Song, MusicVideo, PerformanceVideo, Podcast, Outfit, Cover),
)

Coverable = strawberry.union(
    "Coverable",
    (Project, Podcast),
)