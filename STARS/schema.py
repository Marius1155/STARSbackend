import graphene
from graphene_django import DjangoObjectType
from .models import *

class ArtistType(DjangoObjectType):
    class Meta:
        model = Artist
        filter_fields = {
            "name": ["exact", "icontains", "istartswith"],
            "is_featured": ["exact"],
        }
        interfaces = (graphene.relay.Node,)

class ProjectType(DjangoObjectType):
    class Meta:
        model = Project
        filter_fields = {
            "title": ["icontains", "exact"],
            "type": ["exact"],
            "is_featured": ["exact"],
            "release_date": ["exact", "gte", "lte"],
            "artists__name": ["icontains"],
        }
        interfaces = (graphene.relay.Node,)

class SongType(DjangoObjectType):
    class Meta:
        model = Song
        filter_fields = {
            "title": ["icontains", "exact"],
            "release_date": ["exact", "gte", "lte"],
            "is_featured": ["exact"],
            "artists__name": ["icontains"],
        }
        interfaces = (graphene.relay.Node,)

class ProjectSongType(DjangoObjectType):
    class Meta:
        model = ProjectSong
        filter_fields = ["project", "song", "position"]
        interfaces = (graphene.relay.Node,)

class PodcastType(DjangoObjectType):
    class Meta:
        model = Podcast
        filter_fields = ["title", "is_featured"]
        interfaces = (graphene.relay.Node,)

class OutfitType(DjangoObjectType):
    class Meta:
        model = Outfit
        filter_fields = ["artist__name", "date", "is_featured"]
        interfaces = (graphene.relay.Node,)

class ReviewType(DjangoObjectType):
    class Meta:
        model = Review
        filter_fields = ["user__username", "stars", "is_latest", "date_created"]
        interfaces = (graphene.relay.Node,)

class SubReviewType(DjangoObjectType):
    class Meta:
        model = SubReview
        filter_fields = ["topic", "stars"]
        interfaces = (graphene.relay.Node,)

class ProfileType(DjangoObjectType):
    class Meta:
        model = Profile
        filter_fields = ["user__username", "hasPremium"]
        interfaces = (graphene.relay.Node,)

class MessageType(DjangoObjectType):
    class Meta:
        model = Message
        filter_fields = ["sender__username", "receiver__username", "conversation"]
        interfaces = (graphene.relay.Node,)

class ConversationType(DjangoObjectType):
    class Meta:
        model = Conversation
        filter_fields = ["participants__username"]
        interfaces = (graphene.relay.Node,)

class EventType(DjangoObjectType):
    class Meta:
        model = Event
        filter_fields = ["name", "date", "is_featured"]
        interfaces = (graphene.relay.Node,)

class EventSeriesType(DjangoObjectType):
    class Meta:
        model = EventSeries
        filter_fields = ["name"]
        interfaces = (graphene.relay.Node,)

class CoverType(DjangoObjectType):
    class Meta:
        model = Cover
        filter_fields = []
        interfaces = (graphene.relay.Node,)

class MusicVideoType(DjangoObjectType):
    class Meta:
        model = MusicVideo
        filter_fields = ["title", "releaseDate", "is_featured"]
        interfaces = (graphene.relay.Node,)

class Query(graphene.ObjectType):
    artist = graphene.Field(ArtistType, id=graphene.Int(required=True))
    project = graphene.Field(ProjectType, id=graphene.Int(required=True))
    song = graphene.Field(SongType, id=graphene.Int(required=True))

    # Use relay.ConnectionField for pagination with filtering
    artists = graphene.relay.ConnectionField(ArtistType)
    projects = graphene.relay.ConnectionField(ProjectType)
    songs = graphene.relay.ConnectionField(SongType)
    project_songs = graphene.relay.ConnectionField(ProjectSongType)
    podcasts = graphene.relay.ConnectionField(PodcastType)
    outfits = graphene.relay.ConnectionField(OutfitType)
    reviews = graphene.relay.ConnectionField(ReviewType)
    sub_reviews = graphene.relay.ConnectionField(SubReviewType)
    profiles = graphene.relay.ConnectionField(ProfileType)
    messages = graphene.relay.ConnectionField(MessageType)
    conversations = graphene.relay.ConnectionField(ConversationType)
    events = graphene.relay.ConnectionField(EventType)
    event_series = graphene.relay.ConnectionField(EventSeriesType)
    covers = graphene.relay.ConnectionField(CoverType)
    music_videos = graphene.relay.ConnectionField(MusicVideoType)

schema = graphene.Schema(query=Query)