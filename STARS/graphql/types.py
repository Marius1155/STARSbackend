import strawberry
import strawberry_django
from strawberry.types import Info
from typing import Optional, Iterable, Any, List
from strawberry_django.relay import DjangoCursorConnection
from STARS import models
from django.contrib.auth.models import User as DjangoUser
from asgiref.sync import sync_to_async
from strawberry import relay
from STARS import models

# Import your filters to use them in the fields
from . import filters, orders

@strawberry_django.type(models.Artist, fields="__all__")
class Artist(strawberry.relay.Node):
    song_artists: relay.ListConnection["SongArtist"] = strawberry_django.connection(filters=filters.SongArtistFilter, order=orders.SongArtistOrder)
    project_artists: relay.ListConnection["ProjectArtist"] = strawberry_django.connection(filters=filters.ProjectArtistFilter, order=orders.ProjectArtistOrder)
    outfits: relay.ListConnection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter, order=orders.OutfitOrder)
    podcasts: relay.ListConnection["Podcast"] = strawberry_django.connection(filters=filters.PodcastFilter, order=orders.PodcastOrder)

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
    def get_podcasts(self) -> List[models.Podcast]:
        return self.podcasts.all()


@strawberry_django.type(models.EventSeries, fields="__all__")
class EventSeries(strawberry.relay.Node):
    events: relay.ListConnection["Event"] = strawberry_django.connection(filters=filters.EventFilter, order=orders.EventOrder)

    @sync_to_async
    def get_events(self) -> List[models.Event]:
        return self.events.all()


@strawberry_django.type(models.Event, fields="__all__")
class Event(strawberry.relay.Node):
    series: "EventSeries"
    reviews: relay.ListConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)
    outfits: relay.ListConnection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter, order=orders.OutfitOrder)

    @sync_to_async
    def get_reviews(self) -> List[models.Review]:
        return self.reviews.all()

    @sync_to_async
    def get_outfits(self) -> List[models.Outfit]:
        return self.outfits.all()


@strawberry_django.type(
    DjangoUser,
    fields=["id", "username", "email", "first_name", "is_staff", "is_superuser"]
)
class User(strawberry.relay.Node):
    profile: "Profile"
    conversations: relay.ListConnection["Conversation"] = strawberry_django.connection(filters=filters.ConversationFilter, order=orders.ConversationOrder)
    seen_conversations: relay.ListConnection["Conversation"] = strawberry_django.connection(filters=filters.ConversationFilter, order=orders.ConversationOrder)
    reviews: relay.ListConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)

    @sync_to_async
    def get_conversations(self) -> List[models.Conversation]:
        return self.conversations.all()

    @sync_to_async
    def get_seen_conversations(self) -> List[models.Conversation]:
        return self.seen_conversations.all()

    @sync_to_async
    def get_reviews(self) -> List[models.Review]:
        return self.reviews.all()


@strawberry_django.type(models.Comment, fields="__all__")
class Comment(strawberry.relay.Node):
    review: "Review"
    user: "User"
    liked_by: relay.ListConnection["User"] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)
    disliked_by: relay.ListConnection["User"] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)

    @sync_to_async
    def get_liked_by(self) -> List[models.User]:
        return self.liked_by.all()

    @sync_to_async
    def get_disliked_by(self) -> List[models.User]:
        return self.disliked_by.all()


@strawberry_django.type(models.Review, fields="__all__")
class Review(strawberry.relay.Node):
    user: "User"
    content_object: "Reviewable"
    subreviews: relay.ListConnection["SubReview"] = strawberry_django.connection(filters=filters.SubReviewFilter, order=orders.SubReviewOrder)
    liked_by: relay.ListConnection["User"] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)
    disliked_by: relay.ListConnection["User"] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)

    @sync_to_async
    def get_subreviews(self) -> List[models.SubReview]:
        return self.subreviews.all()

    @sync_to_async
    def get_liked_by(self) -> List[models.User]:
        return self.liked_by.all()

    @sync_to_async
    def get_disliked_by(self) -> List[models.User]:
        return self.disliked_by.all()


@strawberry_django.type(models.SubReview, fields="__all__")
class SubReview(strawberry.relay.Node):
    review: "Review"


@strawberry_django.type(models.Cover, fields="__all__")
class Cover(strawberry.relay.Node):
    content_object: "Coverable"
    reviews: relay.ListConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)

    @sync_to_async
    def get_reviews(self) -> List[models.Review]:
        return self.reviews.all()


@strawberry_django.type(models.MusicVideo, fields="__all__")
class MusicVideo(strawberry.relay.Node):
    songs: relay.ListConnection["Song"] = strawberry_django.connection(filters=filters.SongFilter, order=orders.SongOrder)
    reviews: relay.ListConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)
    outfits: relay.ListConnection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter, order=orders.OutfitOrder)

    @sync_to_async
    def get_songs(self) -> List[models.Song]:
        return self.songs.all()

    @sync_to_async
    def get_reviews(self) -> List[models.Review]:
        return self.reviews.all()

    @sync_to_async
    def get_outfits(self) -> List[models.Outfit]:
        return self.outfits.all()


@strawberry_django.type(models.Song, fields="__all__")
class Song(strawberry.relay.Node):
    alternative_versions: relay.ListConnection["Song"] = strawberry_django.connection(filters=filters.SongFilter, order=orders.SongOrder)
    song_artists: relay.ListConnection["SongArtist"] = strawberry_django.connection(filters=filters.SongArtistFilter, order=orders.SongArtistOrder)
    project_songs: relay.ListConnection["ProjectSong"] = strawberry_django.connection(filters=filters.ProjectSongFilter, order=orders.ProjectSongOrder)
    music_videos: relay.ListConnection["MusicVideo"] = strawberry_django.connection(filters=filters.MusicVideoFilter, order=orders.MusicVideoOrder)
    reviews: relay.ListConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)

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
    def get_reviews(self) -> List[models.Review]:
        return self.reviews.all()


@strawberry_django.type(models.SongArtist, fields="__all__")
class SongArtist(strawberry.relay.Node):
    song: "Song"
    artist: "Artist"


# --- Final Project type with field annotations and connection values ---

@strawberry_django.type(models.Project, fields="__all__")
class Project(relay.Node):
    covers: relay.ListConnection["Cover"] = strawberry_django.connection(filters=filters.CoverFilter, order=orders.CoverOrder)
    project_songs: relay.ListConnection["ProjectSong"] = strawberry_django.connection(filters=filters.ProjectSongFilter, order=orders.ProjectSongOrder)
    project_artists: relay.ListConnection["ProjectArtist"] = strawberry_django.connection(filters=filters.ProjectArtistFilter, order=orders.ProjectArtistOrder)
    reviews: relay.ListConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)
    alternative_versions: relay.ListConnection["Project"] = strawberry_django.connection(filters=filters.ProjectFilter, order=orders.ProjectOrder)

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
    hosts: relay.ListConnection["Artist"] = strawberry_django.connection(filters=filters.ArtistFilter, order=orders.ArtistOrder)
    covers: relay.ListConnection["Cover"] = strawberry_django.connection(filters=filters.CoverFilter, order=orders.CoverOrder)
    reviews: relay.ListConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)

    @sync_to_async
    def get_hosts(self) -> List[models.Artist]:
        return self.hosts.all()

    @sync_to_async
    def get_covers(self) -> List[models.Cover]:
        return self.covers.all()

    @sync_to_async
    def get_reviews(self) -> List[models.Review]:
        return self.reviews.all()


@strawberry_django.type(models.Outfit, fields="__all__")
class Outfit(strawberry.relay.Node):
    artist: "Artist"
    music_videos: relay.ListConnection["MusicVideo"] = strawberry_django.connection(filters=filters.MusicVideoFilter, order=orders.MusicVideoOrder)
    covers: relay.ListConnection["Cover"] = strawberry_django.connection(filters=filters.CoverFilter, order=orders.CoverOrder)
    matches: relay.ListConnection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter, order=orders.OutfitOrder)
    events: relay.ListConnection["Event"] = strawberry_django.connection(filters=filters.EventFilter, order=orders.EventOrder)
    reviews: relay.ListConnection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)

    @sync_to_async
    def get_music_videos(self) -> List[models.MusicVideo]:
        return self.music_videos.all()

    @sync_to_async
    def get_covers(self) -> List[models.Cover]:
        return self.covers.all()

    @sync_to_async
    def get_matches(self) -> List[models.Outfit]:
        return self.matches.all()

    @sync_to_async
    def get_events(self) -> List[models.Event]:
        return self.events.all()

    @sync_to_async
    def get_reviews(self) -> List[models.Review]:
        return self.reviews.all()


@strawberry_django.type(models.Conversation, fields="__all__")
class Conversation(strawberry.relay.Node):
    latest_message: Optional["Message"]
    latest_message_sender: Optional["User"]
    participants: relay.ListConnection["User"] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)
    messages: relay.ListConnection["Message"] = strawberry_django.connection(filters=filters.MessageFilter, order=orders.MessageOrder)
    seen_by: relay.ListConnection["User"] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)

    @sync_to_async
    def get_participants(self) -> List[models.User]:
        return self.participants.all()

    @sync_to_async
    def get_messages(self) -> List[models.Message]:
        return self.messages.all()

    @sync_to_async
    def get_seen_by(self) -> List[models.User]:
        return self.seen_by.all()


@strawberry_django.type(models.Message, fields="__all__")
class Message(strawberry.relay.Node):
    conversation: "Conversation"
    sender: Optional["User"]
    replying_to: Optional["Message"]
    liked_by: relay.ListConnection["User"] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)

    @sync_to_async
    def get_liked_by(self) -> List[models.User]:
        return self.liked_by.all()


@strawberry_django.type(models.Profile, fields="__all__")
class Profile(strawberry.relay.Node):
    user: "User"
    followers: relay.ListConnection["Profile"] = strawberry_django.connection(filters=filters.ProfileFilter, order=orders.ProfileOrder)
    following: relay.ListConnection["Profile"] = strawberry_django.connection(filters=filters.ProfileFilter, order=orders.ProfileOrder)

    @sync_to_async()
    def get_followers(self) -> List[models.Profile]:
        return self.followers.all()

    @sync_to_async
    def get_following(self) -> List[models.Profile]:
        return self.following.all()


# The Unions still work correctly with these simplified types
Reviewable = strawberry.union(
    "Reviewable",
    (Event, Project, Song, MusicVideo, Podcast, Outfit, Cover),
)

Coverable = strawberry.union(
    "Coverable",
    (Project, Podcast),
)