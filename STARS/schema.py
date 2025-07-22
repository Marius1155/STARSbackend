import graphene
from graphene_django import DjangoObjectType
from graphene import relay
from .models import *

class ArtistType(DjangoObjectType):
    class Meta:
        model = Artist
        filter_fields = {
            "name": ["exact", "icontains", "istartswith"],
            "is_featured": ["exact"],
        }
        interfaces = (relay.Node,)

    project_artists = graphene.List(lambda: ProjectArtistType)
    song_artists = graphene.List(lambda: SongArtistType)

    def resolve_project_artists(self, info):
        return self.projectartist_set.all()

    def resolve_song_artists(self, info):
        return self.songartist_set.all()

class ProjectType(DjangoObjectType):
    class Meta:
        model = Project
        filter_fields = {
            "title": ["icontains", "exact"],
            "type": ["exact"],
            "is_featured": ["exact"],
            "release_date": ["exact", "gte", "lte"],
        }
        interfaces = (relay.Node,)

    covers = graphene.List(lambda: CoverType)
    reviews = graphene.List(lambda: ReviewType)
    project_artists = graphene.List(lambda: ProjectArtistType)
    project_songs = graphene.List(lambda: ProjectSongType)

    def resolve_covers(self, info):
        return self.covers.all()

    def resolve_reviews(self, info):
        return self.reviews.all()

    def resolve_project_artists(self, info):
        return self.projectartist_set.all()

    def resolve_project_songs(self, info):
        return self.projectsong_set.all()

class SongType(DjangoObjectType):
    class Meta:
        model = Song
        filter_fields = {
            "title": ["icontains", "exact"],
            "release_date": ["exact", "gte", "lte"],
            "is_featured": ["exact"],
        }
        interfaces = (relay.Node,)

    reviews = graphene.List(lambda: ReviewType)
    song_artists = graphene.List(lambda: SongArtistType)

    def resolve_reviews(self, info):
        return self.reviews.all()

    def resolve_song_artists(self, info):
        return self.songartist_set.all()

class ProjectSongType(DjangoObjectType):
    class Meta:
        model = ProjectSong
        filter_fields = ["project", "song", "position"]
        interfaces = (relay.Node,)

class ProjectArtistType(DjangoObjectType):
    class Meta:
        model = ProjectArtist
        filter_fields = ["project", "artist", "position"]
        interfaces = (relay.Node,)

class SongArtistType(DjangoObjectType):
    class Meta:
        model = SongArtist
        filter_fields = ["song", "artist", "position"]
        interfaces = (relay.Node,)

class PodcastType(DjangoObjectType):
    class Meta:
        model = Podcast
        filter_fields = ["title", "is_featured"]
        interfaces = (relay.Node,)

    reviews = graphene.List(lambda: ReviewType)
    covers = graphene.List(lambda: CoverType)

    def resolve_reviews(self, info):
        return self.reviews.all()

    def resolve_covers(self, info):
        return self.covers.all()

class OutfitType(DjangoObjectType):
    class Meta:
        model = Outfit
        filter_fields = ["artist__name", "date", "is_featured"]
        interfaces = (relay.Node,)

    reviews = graphene.List(lambda: ReviewType)

    def resolve_reviews(self, info):
        return self.reviews.all()

class ReviewType(DjangoObjectType):
    class Meta:
        model = Review
        filter_fields = ["user__username", "stars", "is_latest", "date_created"]
        interfaces = (relay.Node,)

    subreviews = graphene.List(lambda: SubReviewType)

    def resolve_subreviews(self, info):
        return self.subreviews.all()

class SubReviewType(DjangoObjectType):
    class Meta:
        model = SubReview
        filter_fields = ["topic", "stars"]
        interfaces = (relay.Node,)

class ProfileType(DjangoObjectType):
    class Meta:
        model = Profile
        filter_fields = ["user__username", "hasPremium"]
        interfaces = (relay.Node,)

class MessageType(DjangoObjectType):
    class Meta:
        model = Message
        filter_fields = ["sender__username", "receiver__username", "conversation"]
        interfaces = (relay.Node,)

class ConversationType(DjangoObjectType):
    class Meta:
        model = Conversation
        filter_fields = ["participants__username"]
        interfaces = (relay.Node,)

class EventType(DjangoObjectType):
    class Meta:
        model = Event
        filter_fields = ["name", "date", "is_featured"]
        interfaces = (relay.Node,)

class EventSeriesType(DjangoObjectType):
    class Meta:
        model = EventSeries
        filter_fields = ["name"]
        interfaces = (relay.Node,)

class CoverType(DjangoObjectType):
    class Meta:
        model = Cover
        filter_fields = []
        interfaces = (relay.Node,)

    reviews = graphene.List(lambda: ReviewType)

    def resolve_reviews(self, info):
        return self.reviews.all()

class MusicVideoType(DjangoObjectType):
    class Meta:
        model = MusicVideo
        filter_fields = ["title", "releaseDate", "is_featured"]
        interfaces = (relay.Node,)

    reviews = graphene.List(lambda: ReviewType)

    def resolve_reviews(self, info):
        return self.reviews.all()

# Define Connection classes explicitly
class ArtistConnection(relay.Connection):
    class Meta:
        node = ArtistType

class ProjectConnection(relay.Connection):
    class Meta:
        node = ProjectType

class SongConnection(relay.Connection):
    class Meta:
        node = SongType

class ProjectSongConnection(relay.Connection):
    class Meta:
        node = ProjectSongType

class ProjectArtistConnection(relay.Connection):
    class Meta:
        node = ProjectArtistType

class SongArtistConnection(relay.Connection):
    class Meta:
        node = SongArtistType

class PodcastConnection(relay.Connection):
    class Meta:
        node = PodcastType

class OutfitConnection(relay.Connection):
    class Meta:
        node = OutfitType

class ReviewConnection(relay.Connection):
    class Meta:
        node = ReviewType

class SubReviewConnection(relay.Connection):
    class Meta:
        node = SubReviewType

class ProfileConnection(relay.Connection):
    class Meta:
        node = ProfileType

class MessageConnection(relay.Connection):
    class Meta:
        node = MessageType

class ConversationConnection(relay.Connection):
    class Meta:
        node = ConversationType

class EventConnection(relay.Connection):
    class Meta:
        node = EventType

class EventSeriesConnection(relay.Connection):
    class Meta:
        node = EventSeriesType

class CoverConnection(relay.Connection):
    class Meta:
        node = CoverType

class MusicVideoConnection(relay.Connection):
    class Meta:
        node = MusicVideoType

class Query(graphene.ObjectType):
    artist = graphene.Field(ArtistType, id=graphene.Int(required=True))
    project = graphene.Field(ProjectType, id=graphene.Int(required=True))
    song = graphene.Field(SongType, id=graphene.Int(required=True))

    # Use the explicit Connection classes
    artists = relay.ConnectionField(ArtistConnection)
    projects = relay.ConnectionField(ProjectConnection)
    songs = relay.ConnectionField(SongConnection)
    project_songs = relay.ConnectionField(ProjectSongConnection)
    project_artists = relay.ConnectionField(ProjectArtistConnection)
    song_artists = relay.ConnectionField(SongArtistConnection)
    podcasts = relay.ConnectionField(PodcastConnection)
    outfits = relay.ConnectionField(OutfitConnection)
    reviews = relay.ConnectionField(ReviewConnection)
    sub_reviews = relay.ConnectionField(SubReviewConnection)
    profiles = relay.ConnectionField(ProfileConnection)
    messages = relay.ConnectionField(MessageConnection)
    conversations = relay.ConnectionField(ConversationConnection)
    events = relay.ConnectionField(EventConnection)
    event_series = relay.ConnectionField(EventSeriesConnection)
    covers = relay.ConnectionField(CoverConnection)
    music_videos = relay.ConnectionField(MusicVideoConnection)

schema = graphene.Schema(query=Query)