import strawberry
import strawberry_django
from typing import Optional
from strawberry_django.relay import DjangoCursorConnection
from STARS import models
from django.contrib.auth.models import User as DjangoUser
from asgiref.sync import sync_to_async

# Import your filters to use them in the fields
from . import filters, orders


@strawberry_django.type(models.Artist, fields="__all__")
class Artist(strawberry.relay.Node):
    song_artists: DjangoCursorConnection["SongArtist"] = strawberry_django.connection(filters=filters.SongArtistFilter, order=orders.SongArtistOrder)
    project_artists: DjangoCursorConnection["ProjectArtist"] = strawberry_django.connection(filters=filters.ProjectArtistFilter, order=orders.ProjectArtistOrder)
    outfits: DjangoCursorConnection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter, order=orders.OutfitOrder)
    podcasts: DjangoCursorConnection["Podcast"] = strawberry_django.connection(filters=filters.PodcastFilter, order=orders.PodcastOrder)


@strawberry_django.type(models.EventSeries, fields="__all__")
class EventSeries(strawberry.relay.Node):
    events: DjangoCursorConnection["Event"] = strawberry_django.connection(filters=filters.EventFilter, order=orders.EventOrder)


@strawberry_django.type(models.Event, fields="__all__")
class Event(strawberry.relay.Node):
    series: "EventSeries"
    reviews: DjangoCursorConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)
    outfits: DjangoCursorConnection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter, order=orders.OutfitOrder)


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
    liked_by: DjangoCursorConnection["User"] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)
    disliked_by: DjangoCursorConnection["User"] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)


@strawberry_django.type(models.Review, fields="__all__")
class Review(strawberry.relay.Node):
    user: "User"
    content_object: "Reviewable"
    subreviews: DjangoCursorConnection["SubReview"] = strawberry_django.connection(filters=filters.SubReviewFilter, order=orders.SubReviewOrder)
    liked_by: DjangoCursorConnection["User"] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)
    disliked_by: DjangoCursorConnection["User"] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)


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


@strawberry_django.type(models.Song, fields="__all__")
class Song(strawberry.relay.Node):
    alternative_versions: DjangoCursorConnection["Song"] = strawberry_django.connection(filters=filters.SongFilter, order=orders.SongOrder)
    song_artists: DjangoCursorConnection["SongArtist"] = strawberry_django.connection(filters=filters.SongArtistFilter, order=orders.SongArtistOrder)
    project_songs: DjangoCursorConnection["ProjectSong"] = strawberry_django.connection(filters=filters.ProjectSongFilter, order=orders.ProjectSongOrder)
    music_videos: DjangoCursorConnection["MusicVideo"] = strawberry_django.connection(filters=filters.MusicVideoFilter, order=orders.MusicVideoOrder)
    reviews: DjangoCursorConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)


@strawberry_django.type(models.SongArtist, fields="__all__")
class SongArtist(strawberry.relay.Node):
    song: "Song"
    artist: "Artist"


@strawberry_django.type(models.Project, fields="__all__")
class Project(strawberry.relay.Node):
    covers: DjangoCursorConnection["Cover"] = strawberry_django.connection(filters=filters.CoverFilter, order=orders.CoverOrder)
    alternative_versions: DjangoCursorConnection["Project"] = strawberry_django.connection(filters=filters.ProjectFilter, order=orders.ProjectOrder)
    project_songs: DjangoCursorConnection["ProjectSong"] = strawberry_django.connection(filters=filters.ProjectSongFilter, order=orders.ProjectSongOrder)
    project_artists: DjangoCursorConnection["ProjectArtist"] = strawberry_django.connection(filters=filters.ProjectArtistFilter, order=orders.ProjectArtistOrder)
    reviews: DjangoCursorConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)

    @strawberry_django.field
    async def covers(self, info) -> list["Cover"]:
        return await sync_to_async(list)(self.covers.all())


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
    hosts: DjangoCursorConnection["Artist"] = strawberry_django.connection(filters=filters.ArtistFilter, order=orders.ArtistOrder)
    covers: DjangoCursorConnection["Cover"] = strawberry_django.connection(filters=filters.CoverFilter, order=orders.CoverOrder)
    reviews: DjangoCursorConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)


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


# The Unions still work correctly with these simplified types
Reviewable = strawberry.union(
    "Reviewable",
    (Event, Project, Song, MusicVideo, Podcast, Outfit, Cover),
)

Coverable = strawberry.union(
    "Coverable",
    (Project, Podcast),
)