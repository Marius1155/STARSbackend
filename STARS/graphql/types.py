import strawberry
import strawberry_django
from strawberry.types import Info
from typing import Optional, Iterable, Any, List
from django.db.models import QuerySet, Count, Q
from strawberry_django.relay import DjangoCursorConnection
from STARS import models
from django.contrib.auth.models import User as DjangoUser
from asgiref.sync import sync_to_async
from strawberry import relay
from STARS import models
from django.utils import timezone # Added
from datetime import timedelta # Added
from django.contrib.contenttypes.models import ContentType # Added

# Import your filters to use them in the fields
from . import filters, orders

@strawberry.type
class MusicSearchResponse:
    is_cached: bool
    artists: List["Artist"]
    projects: List["Project"]
    songs: List["Song"]
    music_videos: List["MusicVideo"]
    performance_videos: List["PerformanceVideo"]

@strawberry.type
class PodcastSearchResponse:
    is_cached: bool
    podcasts: List["Podcast"]

@strawberry_django.type(models.MusicGenre, fields="__all__")
class MusicGenre(strawberry.relay.Node):
    project_genres_ordered: DjangoCursorConnection["ProjectGenresOrdered"] = strawberry_django.connection(filters=filters.ProjectGenresOrderedFilter, order=orders.ProjectGenresOrderedOrder)
    song_genres_ordered: DjangoCursorConnection["SongGenresOrdered"] = strawberry_django.connection(filters=filters.SongGenresOrderedFilter, order=orders.SongGenresOrderedOrder)
    artist_genres_ordered: DjangoCursorConnection["ArtistGenresOrdered"] = strawberry_django.connection(filters=filters.ArtistGenresOrderedFilter, order=orders.ArtistGenresOrderedOrder)


@strawberry_django.type(models.ProjectGenresOrdered, fields="__all__")
class ProjectGenresOrdered(strawberry.relay.Node):
    project: "Project"
    genre: "MusicGenre"


@strawberry_django.type(models.SongGenresOrdered, fields="__all__")
class SongGenresOrdered(strawberry.relay.Node):
    song: "Song"
    genre: "MusicGenre"


@strawberry_django.type(models.ArtistGenresOrdered, fields="__all__")
class ArtistGenresOrdered(strawberry.relay.Node):
    artist: "Artist"
    genre: "MusicGenre"


@strawberry_django.type(models.PodcastGenre, fields="__all__")
class PodcastGenre(strawberry.relay.Node):
    podcast_genres_ordered: DjangoCursorConnection["PodcastGenresOrdered"] = strawberry_django.connection(filters=filters.PodcastGenresOrderedFilter, order=orders.PodcastGenresOrderedOrder)


@strawberry_django.type(models.PodcastGenresOrdered, fields="__all__")
class PodcastGenresOrdered(strawberry.relay.Node):
    podcast: "Podcast"
    genre: "PodcastGenre"


@strawberry_django.type(models.Artist, fields="__all__")
class Artist(strawberry.relay.Node):
    # Change DjangoCursorConnection to relay.ListConnection to match your Project type
    song_artists: relay.ListConnection["SongArtist"] = strawberry_django.connection(filters=filters.SongArtistFilter, order=orders.SongArtistOrder)
    project_artists: relay.ListConnection["ProjectArtist"] = strawberry_django.connection(filters=filters.ProjectArtistFilter, order=orders.ProjectArtistOrder)
    outfits: relay.ListConnection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter, order=orders.OutfitOrder)
    performance_videos: relay.ListConnection["PerformanceVideo"] = strawberry_django.connection(filters=filters.PerformanceVideoFilter, order=orders.PerformanceVideoOrder)
    artist_genres_ordered: relay.ListConnection["ArtistGenresOrdered"] = strawberry_django.connection(filters=filters.ArtistGenresOrderedFilter, order=orders.ArtistGenresOrderedOrder)


@strawberry_django.type(models.EventSeries, fields="__all__")
class EventSeries(strawberry.relay.Node):
    user: Optional["User"]
    events: DjangoCursorConnection["Event"] = strawberry_django.connection(filters=filters.EventFilter, order=orders.EventOrder)


@strawberry_django.type(models.Event, fields="__all__")
class Event(strawberry.relay.Node):
    user: Optional["User"]
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
    covers_added: DjangoCursorConnection["Cover"] = strawberry_django.connection(filters=filters.CoverFilter, order=orders.CoverOrder)


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


@strawberry_django.type(models.RankedItem, fields="__all__")
class RankedItem(strawberry.relay.Node):
    content_object: "Reviewable"


@strawberry_django.type(models.RankedList, fields="__all__")
class RankedList(strawberry.relay.Node):
    items: relay.ListConnection["RankedItem"] = strawberry_django.connection()


@strawberry_django.type(models.Review, fields="__all__")
class Review(strawberry.relay.Node):
    user: "User"
    content_object: Optional["Reviewable"]
    ranked_list: Optional["RankedList"]

    subreviews: DjangoCursorConnection["SubReview"] = strawberry_django.connection(filters=filters.SubReviewFilter, order=orders.SubReviewOrder)
    comments: DjangoCursorConnection["Comment"] = strawberry_django.connection(filters=filters.CommentFilter, order=orders.CommentOrder)
    liked_by: DjangoCursorConnection["User"] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)
    disliked_by: DjangoCursorConnection["User"] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)

    @strawberry.field
    def is_post(self) -> bool:
        return self.content_type is None

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
        if self.content_type is None:
            return False

        def check():
            return models.Review.objects.filter(
                user=self.user,
                content_type=self.content_type,
                object_id=self.object_id,
                date_created__lt=self.date_created
            ).exists()

        return await sync_to_async(check)()


SubReviewTopic = strawberry.enum(models.SubReview.Topic)

@strawberry.type
class TopicMapping:
    model_name: str
    allowed_topics: List[SubReviewTopic]


@strawberry_django.type(models.SubReview, fields="__all__")
class SubReview(strawberry.relay.Node):
    review: "Review"
    topic: SubReviewTopic


@strawberry_django.type(models.Cover, fields="__all__")
class Cover(strawberry.relay.Node):
    content_object: "Coverable"
    reviews: DjangoCursorConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)
    user: Optional["User"]


@strawberry_django.type(models.MusicVideo, fields="__all__")
class MusicVideo(strawberry.relay.Node):
    user: Optional["User"]
    songs: DjangoCursorConnection["Song"] = strawberry_django.connection(filters=filters.SongFilter, order=orders.SongOrder)
    reviews: DjangoCursorConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)
    outfits: DjangoCursorConnection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter, order=orders.OutfitOrder)


@strawberry_django.type(models.PerformanceVideo, fields="__all__")
class PerformanceVideo(strawberry.relay.Node):
    user: Optional["User"]
    event: Optional["Event"]
    artists: DjangoCursorConnection["Artist"] = strawberry_django.connection(filters=filters.ArtistFilter, order=orders.ArtistOrder)
    songs: DjangoCursorConnection["Song"] = strawberry_django.connection(filters=filters.SongFilter, order=orders.SongOrder)
    reviews: DjangoCursorConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)
    outfits: DjangoCursorConnection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter, order=orders.OutfitOrder)


@strawberry_django.type(models.Song, fields="__all__")
class Song(strawberry.relay.Node):
    user: Optional["User"]
    alternative_versions: relay.ListConnection["Song"] = strawberry_django.connection(filters=filters.SongFilter, order=orders.SongOrder)
    song_artists: relay.ListConnection["SongArtist"] = strawberry_django.connection(filters=filters.SongArtistFilter, order=orders.SongArtistOrder)
    project_songs: relay.ListConnection["ProjectSong"] = strawberry_django.connection(filters=filters.ProjectSongFilter, order=orders.ProjectSongOrder)
    music_videos: relay.ListConnection["MusicVideo"] = strawberry_django.connection(filters=filters.MusicVideoFilter, order=orders.MusicVideoOrder)
    performance_videos: relay.ListConnection["PerformanceVideo"] = strawberry_django.connection(filters=filters.PerformanceVideoFilter, order=orders.PerformanceVideoOrder)
    reviews: relay.ListConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)
    song_genres_ordered: relay.ListConnection["SongGenresOrdered"] = strawberry_django.connection(filters=filters.SongGenresOrderedFilter, order=orders.SongGenresOrderedOrder)


@strawberry_django.type(models.SongArtist, fields="__all__")
class SongArtist(strawberry.relay.Node):
    song: "Song"
    artist: "Artist"


@strawberry_django.type(models.Project, fields="__all__")
class Project(relay.Node):
    user: Optional["User"]
    covers: relay.ListConnection["Cover"] = strawberry_django.connection(filters=filters.CoverFilter, order=orders.CoverOrder)
    project_songs: relay.ListConnection["ProjectSong"] = strawberry_django.connection(filters=filters.ProjectSongFilter, order=orders.ProjectSongOrder)
    project_artists: relay.ListConnection["ProjectArtist"] = strawberry_django.connection(filters=filters.ProjectArtistFilter, order=orders.ProjectArtistOrder)
    reviews: relay.ListConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)
    alternative_versions: relay.ListConnection["Project"] = strawberry_django.connection(filters=filters.ProjectFilter, order=orders.ProjectOrder)
    project_genres_ordered: relay.ListConnection["ProjectGenresOrdered"] = strawberry_django.connection(filters=filters.ProjectGenresOrderedFilter, order=orders.ProjectGenresOrderedOrder)


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
    user: Optional["User"]
    covers: relay.ListConnection["Cover"] = strawberry_django.connection(filters=filters.CoverFilter, order=orders.CoverOrder)
    reviews: relay.ListConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)
    podcast_genres_ordered: relay.ListConnection["PodcastGenresOrdered"] = strawberry_django.connection(filters=filters.PodcastGenresOrderedFilter, order=orders.PodcastGenresOrderedOrder)


@strawberry_django.type(models.Outfit, fields="__all__")
class Outfit(strawberry.relay.Node):
    user: Optional["User"]
    artist: "Artist"
    music_videos: relay.ListConnection["MusicVideo"] = strawberry_django.connection(filters=filters.MusicVideoFilter, order=orders.MusicVideoOrder)
    covers: relay.ListConnection["Cover"] = strawberry_django.connection(filters=filters.CoverFilter, order=orders.CoverOrder)
    matches: relay.ListConnection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter, order=orders.OutfitOrder)
    events: relay.ListConnection["Event"] = strawberry_django.connection(filters=filters.EventFilter, order=orders.EventOrder)
    reviews: relay.ListConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)


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


@strawberry_django.type(models.Report, fields="__all__")
class Report(strawberry.relay.Node):
    content_object = "Reportable"
    user: "User"

@strawberry.type
class CreateReportPayload:
    created_successfully: bool

Reviewable = strawberry.union(
    "Reviewable",
    (Event, Project, Song, MusicVideo, PerformanceVideo, Podcast, Outfit, Cover),
)

Coverable = strawberry.union(
    "Coverable",
    (Project, Podcast),
)

Reportable = strawberry.union(
    "Reportable",
    (Artist, Project, Podcast, MusicVideo, PerformanceVideo, Outfit, Review, Event, EventSeries),
)