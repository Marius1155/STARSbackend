import strawberry
import strawberry_django
from strawberry import relay
from strawberry.types import Info
from typing import Iterable, Optional
from STARS import models
from django.contrib.auth.models import User as DjangoUser

# Import your filters to use them in the fields
from . import filters


# Helper function to resolve nodes efficiently and correctly handle IDs
def resolve_model_nodes(model, node_ids, required=False):
    # The library provides the raw, decoded ID to this function
    qs = model.objects.filter(pk__in=node_ids)
    nodes_map = {str(n.pk): n for n in qs}
    return [nodes_map.get(str(pk)) for pk in node_ids]


@strawberry_django.type(models.Artist)
class Artist(relay.Node):
    id: relay.NodeID[int]
    name: strawberry.auto
    picture: strawberry.auto
    bio: strawberry.auto
    wikipedia: strawberry.auto
    pronouns: strawberry.auto
    birthdate: strawberry.auto
    origin: strawberry.auto
    website: strawberry.auto
    facebook: strawberry.auto
    instagram: strawberry.auto
    twitter: strawberry.auto
    youtube_channel: strawberry.auto
    spotify: strawberry.auto
    apple_music: strawberry.auto
    youtube_music: strawberry.auto
    tidal: strawberry.auto
    deezer: strawberry.auto
    soundcloud: strawberry.auto
    bandcamp: strawberry.auto
    is_featured: strawberry.auto

    song_artists: list["SongArtist"] = strawberry_django.field(filters=filters.SongArtistFilter)
    project_artists: list["ProjectArtist"] = strawberry_django.field(filters=filters.ProjectArtistFilter)
    outfits: list["Outfit"] = strawberry_django.field(filters=filters.OutfitFilter)
    podcasts: list["Podcast"] = strawberry_django.field(filters=filters.PodcastFilter)

    @classmethod
    def resolve_node(cls, *, node_id: str, info: Info, required: bool = False) -> Optional["Artist"]:
        return models.Artist.objects.filter(pk=node_id).first()

    @classmethod
    def resolve_nodes(cls, *, info: Info, node_ids: Iterable[str], required: bool = False):
        return resolve_model_nodes(models.Artist, node_ids, required)


@strawberry_django.type(models.EventSeries)
class EventSeries(relay.Node):
    id: relay.NodeID[int]
    name: strawberry.auto
    description: strawberry.auto
    is_featured: strawberry.auto
    events: relay.Connection["Event"] = strawberry_django.connection(filters=filters.EventFilter)

    @classmethod
    def resolve_node(cls, *, node_id: str, info: Info, required: bool = False) -> Optional["EventSeries"]:
        return models.EventSeries.objects.filter(pk=node_id).first()

    @classmethod
    def resolve_nodes(cls, *, info: Info, node_ids: Iterable[str], required: bool = False):
        return resolve_model_nodes(models.EventSeries, node_ids, required)


@strawberry_django.type(models.Event)
class Event(relay.Node):
    id: relay.NodeID[int]
    series: "EventSeries"
    name: strawberry.auto
    date: strawberry.auto
    location: strawberry.auto
    is_one_time: strawberry.auto
    reviews_count: strawberry.auto
    star_average: strawberry.auto
    is_featured: strawberry.auto
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)
    outfits: relay.Connection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter)

    @classmethod
    def resolve_node(cls, *, node_id: str, info: Info, required: bool = False) -> Optional["Event"]:
        return models.Event.objects.filter(pk=node_id).first()

    @classmethod
    def resolve_nodes(cls, *, info: Info, node_ids: Iterable[str], required: bool = False):
        return resolve_model_nodes(models.Event, node_ids, required)


@strawberry_django.type(DjangoUser)
class User(relay.Node):
    id: relay.NodeID[int]
    username: strawberry.auto
    email: strawberry.auto
    first_name: strawberry.auto
    last_name: strawberry.auto
    profile: "Profile"
    conversations: relay.Connection["Conversation"] = strawberry_django.connection(filters=filters.ConversationFilter)
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)

    @classmethod
    def resolve_node(cls, *, node_id: str, info: Info, required: bool = False) -> Optional[DjangoUser]:
        return DjangoUser.objects.filter(pk=node_id).first()

    @classmethod
    def resolve_nodes(cls, *, info: Info, node_ids: Iterable[str], required: bool = False):
        return resolve_model_nodes(DjangoUser, node_ids, required)


@strawberry_django.type(models.Review)
class Review(relay.Node):
    id: relay.NodeID[int]
    user: "User"
    stars: strawberry.auto
    text: strawberry.auto
    date_created: strawberry.auto
    date_updated: strawberry.auto
    is_latest: strawberry.auto
    content_object: "Reviewable"
    subreviews: list["SubReview"] = strawberry_django.field(filters=filters.SubReviewFilter)

    @classmethod
    def resolve_node(cls, *, node_id: str, info: Info, required: bool = False) -> Optional["Review"]:
        return models.Review.objects.filter(pk=node_id).first()

    @classmethod
    def resolve_nodes(cls, *, info: Info, node_ids: Iterable[str], required: bool = False):
        return resolve_model_nodes(models.Review, node_ids, required)


@strawberry_django.type(models.SubReview, fields="__all__")
class SubReview:
    review: "Review"


@strawberry_django.type(models.Cover)
class Cover(relay.Node):
    id: relay.NodeID[int]
    image: strawberry.auto
    reviews_count: strawberry.auto
    star_average: strawberry.auto
    is_featured: strawberry.auto
    content_object: "Coverable"
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)

    @classmethod
    def resolve_node(cls, *, node_id: str, info: Info, required: bool = False) -> Optional["Cover"]:
        return models.Cover.objects.filter(pk=node_id).first()

    @classmethod
    def resolve_nodes(cls, *, info: Info, node_ids: Iterable[str], required: bool = False):
        return resolve_model_nodes(models.Cover, node_ids, required)


@strawberry_django.type(models.MusicVideo)
class MusicVideo(relay.Node):
    id: relay.NodeID[int]
    title: strawberry.auto
    release_date: strawberry.auto
    youtube: strawberry.auto
    thumbnail: strawberry.auto
    reviews_count: strawberry.auto
    star_average: strawberry.auto
    is_featured: strawberry.auto
    songs: list["Song"] = strawberry_django.field(filters=filters.SongFilter)
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)
    outfits: relay.Connection["Outfit"] = strawberry_django.connection(filters=filters.OutfitFilter)

    @classmethod
    def resolve_node(cls, *, node_id: str, info: Info, required: bool = False) -> Optional["MusicVideo"]:
        return models.MusicVideo.objects.filter(pk=node_id).first()

    @classmethod
    def resolve_nodes(cls, *, info: Info, node_ids: Iterable[str], required: bool = False):
        return resolve_model_nodes(models.MusicVideo, node_ids, required)


@strawberry_django.type(models.Song)
class Song(relay.Node):
    id: relay.NodeID[int]
    title: strawberry.auto
    length: strawberry.auto
    preview: strawberry.auto
    release_date: strawberry.auto
    reviews_count: strawberry.auto
    star_average: strawberry.auto
    is_featured: strawberry.auto
    alternative_versions: list["Song"] = strawberry_django.field(filters=filters.SongFilter)
    song_artists: list["SongArtist"] = strawberry_django.field(filters=filters.SongArtistFilter)
    project_songs: list["ProjectSong"] = strawberry_django.field(filters=filters.ProjectSongFilter)
    music_videos: list["MusicVideo"] = strawberry_django.field(filters=filters.MusicVideoFilter)
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)

    @classmethod
    def resolve_node(cls, *, node_id: str, info: Info, required: bool = False) -> Optional["Song"]:
        return models.Song.objects.filter(pk=node_id).first()

    @classmethod
    def resolve_nodes(cls, *, info: Info, node_ids: Iterable[str], required: bool = False):
        return resolve_model_nodes(models.Song, node_ids, required)


@strawberry_django.type(models.SongArtist, fields="__all__")
class SongArtist:
    song: "Song"
    artist: "Artist"


@strawberry_django.type(models.Project)
class Project(relay.Node):
    id: relay.NodeID[int]
    title: strawberry.auto
    number_of_songs: strawberry.auto
    release_date: strawberry.auto
    project_type: strawberry.auto
    length: strawberry.auto
    reviews_count: strawberry.auto
    star_average: strawberry.auto
    spotify: strawberry.auto
    apple_music: strawberry.auto
    youtube_music: strawberry.auto
    tidal: strawberry.auto
    deezer: strawberry.auto
    soundcloud: strawberry.auto
    bandcamp: strawberry.auto
    is_featured: strawberry.auto
    covers: list["Cover"] = strawberry_django.field(filters=filters.CoverFilter)
    alternative_versions: list["Project"] = strawberry_django.field(filters=filters.ProjectFilter)
    project_songs: list["ProjectSong"] = strawberry_django.field(filters=filters.ProjectSongFilter)
    project_artists: list["ProjectArtist"] = strawberry_django.field(filters=filters.ProjectArtistFilter)
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)

    @classmethod
    def resolve_node(cls, *, node_id: str, info: Info, required: bool = False) -> Optional["Project"]:
        return models.Project.objects.filter(pk=node_id).first()

    @classmethod
    def resolve_nodes(cls, *, info: Info, node_ids: Iterable[str], required: bool = False):
        return resolve_model_nodes(models.Project, node_ids, required)


@strawberry_django.type(models.ProjectArtist, fields="__all__")
class ProjectArtist:
    project: "Project"
    artist: "Artist"


@strawberry_django.type(models.ProjectSong, fields="__all__")
class ProjectSong:
    project: "Project"
    song: "Song"


@strawberry_django.type(models.Podcast)
class Podcast(relay.Node):
    id: relay.NodeID[int]
    title: strawberry.auto
    description: strawberry.auto
    since: strawberry.auto
    website: strawberry.auto
    spotify: strawberry.auto
    apple_podcasts: strawberry.auto
    youtube: strawberry.auto
    youtube_music: strawberry.auto
    reviews_count: strawberry.auto
    star_average: strawberry.auto
    is_featured: strawberry.auto
    hosts: list["Artist"] = strawberry_django.field(filters=filters.ArtistFilter)
    covers: list["Cover"] = strawberry_django.field(filters=filters.CoverFilter)
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)

    @classmethod
    def resolve_node(cls, *, node_id: str, info: Info, required: bool = False) -> Optional["Podcast"]:
        return models.Podcast.objects.filter(pk=node_id).first()

    @classmethod
    def resolve_nodes(cls, *, info: Info, node_ids: Iterable[str], required: bool = False):
        return resolve_model_nodes(models.Podcast, node_ids, required)


@strawberry_django.type(models.Outfit)
class Outfit(relay.Node):
    id: relay.NodeID[int]
    artist: "Artist"
    description: strawberry.auto
    date: strawberry.auto
    preview_picture: strawberry.auto
    instagram_post: strawberry.auto
    reviews_count: strawberry.auto
    star_average: strawberry.auto
    is_featured: strawberry.auto
    music_videos: list["MusicVideo"] = strawberry_django.field(filters=filters.MusicVideoFilter)
    covers: list["Cover"] = strawberry_django.field(filters=filters.CoverFilter)
    matches: list["Outfit"] = strawberry_django.field(filters=filters.OutfitFilter)
    events: relay.Connection["Event"] = strawberry_django.connection(filters=filters.EventFilter)
    reviews: relay.Connection["Review"] = strawberry_django.connection(filters=filters.ReviewFilter)

    @classmethod
    def resolve_node(cls, *, node_id: str, info: Info, required: bool = False) -> Optional["Outfit"]:
        return models.Outfit.objects.filter(pk=node_id).first()

    @classmethod
    def resolve_nodes(cls, *, info: Info, node_ids: Iterable[str], required: bool = False):
        return resolve_model_nodes(models.Outfit, node_ids, required)


@strawberry_django.type(models.Conversation)
class Conversation(relay.Node):
    id: relay.NodeID[int]
    latest_message: Optional["Message"]
    latest_message_sender: Optional["User"]
    latest_message_text: strawberry.auto
    latest_message_time: strawberry.auto
    participants: list["User"] = strawberry_django.field(filters=filters.UserFilter)
    messages: relay.Connection["Message"] = strawberry_django.connection(filters=filters.MessageFilter)

    @classmethod
    def resolve_node(cls, *, node_id: str, info: Info, required: bool = False) -> Optional["Conversation"]:
        return models.Conversation.objects.filter(pk=node_id).first()

    @classmethod
    def resolve_nodes(cls, *, info: Info, node_ids: Iterable[str], required: bool = False):
        return resolve_model_nodes(models.Conversation, node_ids, required)


@strawberry_django.type(models.Message)
class Message(relay.Node):
    id: relay.NodeID[int]
    conversation: "Conversation"
    sender: Optional["User"]
    replying_to: Optional["Message"]
    text: strawberry.auto
    time: strawberry.auto
    is_pending: strawberry.auto
    is_delivered: strawberry.auto
    is_read: strawberry.auto
    liked_by: list["User"] = strawberry_django.field(filters=filters.UserFilter)

    @classmethod
    def resolve_node(cls, *, node_id: str, info: Info, required: bool = False) -> Optional["Message"]:
        return models.Message.objects.filter(pk=node_id).first()

    @classmethod
    def resolve_nodes(cls, *, info: Info, node_ids: Iterable[str], required: bool = False):
        return resolve_model_nodes(models.Message, node_ids, required)


@strawberry_django.type(models.Profile, fields="__all__")
class Profile:
    user: "User"
    followers: list["Profile"] = strawberry_django.field(filters=filters.ProfileFilter)
    following: list["Profile"] = strawberry_django.field(filters=filters.ProfileFilter)


# The Unions still need to be defined with their members
Reviewable = strawberry.union(
    "Reviewable",
    (Event, Project, Song, MusicVideo, Podcast, Outfit, Cover),
)

Coverable = strawberry.union(
    "Coverable",
    (Project, Podcast),
)