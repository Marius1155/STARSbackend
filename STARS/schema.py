import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import *

class ArtistType(DjangoObjectType):
    class Meta:
        model = Artist
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "name": ["exact", "icontains", "istartswith"],
            "is_featured": ["exact"],
        }

class ProjectType(DjangoObjectType):
    class Meta:
        model = Project
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "title": ["icontains", "exact"],
            "type": ["exact"],
            "is_featured": ["exact"],
            "release_date": ["exact", "gte", "lte"],
            "artists__name": ["icontains"],
        }

class SongType(DjangoObjectType):
    class Meta:
        model = Song
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "title": ["icontains", "exact"],
            "release_date": ["exact", "gte", "lte"],
            "is_featured": ["exact"],
            "artists__name": ["icontains"],
        }

class ProjectSongType(DjangoObjectType):
    class Meta:
        model = ProjectSong
        interfaces = (graphene.relay.Node,)
        filter_fields = ["project", "song", "position"]

class PodcastType(DjangoObjectType):
    class Meta:
        model = Podcast
        interfaces = (graphene.relay.Node,)
        filter_fields = ["title", "is_featured"]

class OutfitType(DjangoObjectType):
    class Meta:
        model = Outfit
        interfaces = (graphene.relay.Node,)
        filter_fields = ["artist__name", "date", "is_featured"]

class ReviewType(DjangoObjectType):
    class Meta:
        model = Review
        interfaces = (graphene.relay.Node,)
        filter_fields = ["user__username", "stars", "is_latest", "date_created"]

class SubReviewType(DjangoObjectType):
    class Meta:
        model = SubReview
        interfaces = (graphene.relay.Node,)
        filter_fields = ["topic", "stars"]

class ProfileType(DjangoObjectType):
    class Meta:
        model = Profile
        interfaces = (graphene.relay.Node,)
        filter_fields = ["user__username", "hasPremium"]

class MessageType(DjangoObjectType):
    class Meta:
        model = Message
        interfaces = (graphene.relay.Node,)
        filter_fields = ["sender__username", "receiver__username", "conversation"]

class ConversationType(DjangoObjectType):
    class Meta:
        model = Conversation
        interfaces = (graphene.relay.Node,)
        filter_fields = ["participants__username"]

class EventType(DjangoObjectType):
    class Meta:
        model = Event
        interfaces = (graphene.relay.Node,)
        filter_fields = ["name", "date", "is_featured"]

class EventSeriesType(DjangoObjectType):
    class Meta:
        model = EventSeries
        interfaces = (graphene.relay.Node,)
        filter_fields = ["name"]

class CoverType(DjangoObjectType):
    class Meta:
        model = Cover
        interfaces = (graphene.relay.Node,)
        filter_fields = []

class MusicVideoType(DjangoObjectType):
    class Meta:
        model = MusicVideo
        interfaces = (graphene.relay.Node,)
        filter_fields = ["title", "releaseDate", "is_featured"]

# --- Root Query with DjangoFilterConnectionField ---

class Query(graphene.ObjectType):
    artist = graphene.relay.Node.Field(ArtistType)
    project = graphene.relay.Node.Field(ProjectType)
    song = graphene.relay.Node.Field(SongType)

    artists = DjangoFilterConnectionField(ArtistType)
    projects = DjangoFilterConnectionField(ProjectType)
    songs = DjangoFilterConnectionField(SongType)
    project_songs = DjangoFilterConnectionField(ProjectSongType)
    podcasts = DjangoFilterConnectionField(PodcastType)
    outfits = DjangoFilterConnectionField(OutfitType)
    reviews = DjangoFilterConnectionField(ReviewType)
    sub_reviews = DjangoFilterConnectionField(SubReviewType)
    profiles = DjangoFilterConnectionField(ProfileType)
    messages = DjangoFilterConnectionField(MessageType)
    conversations = DjangoFilterConnectionField(ConversationType)
    events = DjangoFilterConnectionField(EventType)
    event_series = DjangoFilterConnectionField(EventSeriesType)
    covers = DjangoFilterConnectionField(CoverType)
    music_videos = DjangoFilterConnectionField(MusicVideoType)

schema = graphene.Schema(query=Query)