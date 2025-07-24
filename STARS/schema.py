'''import strawberry
from typing import Optional, List
from strawberry import auto
from strawberry_django import filter
import strawberry_django
from .models import *

@strawberry_django.filter(Artist)
class ArtistFilter:
    name: Optional[str] = strawberry_django.filter.lookups(["exact", "icontains", "istartswith"])
    is_featured: Optional[bool] = strawberry_django.filter.lookups(["exact"])


@strawberry_django.type(Artist, filters=ArtistFilter)
class ArtistType:
    id: auto
    name: auto
    picture: auto
    is_featured: auto

    @strawberry.field
    def project_artists(self) -> List["ProjectArtistType"]:
        return list(self.projectartist_set.all())

    @strawberry.field
    def song_artists(self) -> List["SongArtistType"]:
        return list(self.songartist_set.all())


# If you also want connection-based pagination
@strawberry.type
class ArtistConnection:
    edges: List[ArtistType]


# Mutations
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_artist(self, name: str, picture: str) -> ArtistType:
        artist = Artist(name=name, picture=picture)
        artist.save()
        return artist

    @strawberry.mutation
    def update_artist(self, id: strawberry.ID, name: Optional[str] = None, picture: Optional[str] = None,
                      is_featured: Optional[bool] = None) -> ArtistType:
        artist = Artist.objects.get(pk=id)
        if name is not None:
            artist.name = name
        if picture is not None:
            artist.picture = picture
        if is_featured is not None:
            artist.is_featured = is_featured
        artist.save()
        return artist

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

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")

class ProfileType(DjangoObjectType):
    class Meta:
        model = Profile
        filter_fields = ["user__username", "hasPremium"]
        interfaces = (relay.Node,)

    user = graphene.Field(UserType)  # Expose user

    def resolve_user(self, info):
        return self.user

class MessageType(DjangoObjectType):
    class Meta:
        model = Message
        filter_fields = ["sender__username", "conversation"]
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
    artist = graphene.Field(ArtistType, id=graphene.ID(required=True))
    project = graphene.Field(ProjectType, id=graphene.ID(required=True))
    song = graphene.Field(SongType, id=graphene.ID(required=True))
    project_song = graphene.Field(ProjectSongType, id=graphene.ID(required=True))
    project_artist = graphene.Field(ProjectArtistType, id=graphene.ID(required=True))
    song_artist = graphene.Field(SongArtistType, id=graphene.ID(required=True))
    podcast = graphene.Field(PodcastType, id=graphene.ID(required=True))
    outfit = graphene.Field(OutfitType, id=graphene.ID(required=True))
    review = graphene.Field(ReviewType, id=graphene.ID(required=True))
    sub_review = graphene.Field(SubReviewType, id=graphene.ID(required=True))
    profile = graphene.Field(ProfileType, id=graphene.ID(required=True))
    message = graphene.Field(MessageType, id=graphene.ID(required=True))
    conversation = graphene.Field(ConversationType, id=graphene.ID(required=True))
    event = graphene.Field(EventType, id=graphene.ID(required=True))
    event_series = graphene.Field(EventSeriesType, id=graphene.ID(required=True))
    cover = graphene.Field(CoverType, id=graphene.ID(required=True))
    music_video = graphene.Field(MusicVideoType, id=graphene.ID(required=True))

    # List queries with Relay pagination (keep as is)
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

    # Resolver methods for single items
    def resolve_artist(self, info, id):
        return Artist.objects.get(pk=id)

    def resolve_project(self, info, id):
        return Project.objects.get(pk=id)

    def resolve_song(self, info, id):
        return Song.objects.get(pk=id)

    def resolve_project_song(self, info, id):
        return ProjectSong.objects.get(pk=id)

    def resolve_project_artist(self, info, id):
        return ProjectArtist.objects.get(pk=id)

    def resolve_song_artist(self, info, id):
        return SongArtist.objects.get(pk=id)

    def resolve_podcast(self, info, id):
        return Podcast.objects.get(pk=id)

    def resolve_outfit(self, info, id):
        return Outfit.objects.get(pk=id)

    def resolve_review(self, info, id):
        return Review.objects.get(pk=id)

    def resolve_sub_review(self, info, id):
        return SubReview.objects.get(pk=id)

    def resolve_profile(self, info, id):
        return Profile.objects.get(pk=id)

    def resolve_message(self, info, id):
        return Message.objects.get(pk=id)

    def resolve_conversation(self, info, id):
        return Conversation.objects.get(pk=id)

    def resolve_event(self, info, id):
        return Event.objects.get(pk=id)

    def resolve_event_series(self, info, id):
        return EventSeries.objects.get(pk=id)

    def resolve_cover(self, info, id):
        return Cover.objects.get(pk=id)

    def resolve_music_video(self, info, id):
        return MusicVideo.objects.get(pk=id)


# ==== ARTIST ====

class CreateArtist(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        picture = graphene.String(required=True)

    artist = graphene.Field(lambda: ArtistType)

    def mutate(self, info, name, picture, **kwargs):
        artist = Artist(name=name, picture=picture, **kwargs)
        artist.save()
        return CreateArtist(artist=artist)

class UpdateArtist(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    artist = graphene.Field(lambda: ArtistType)

    def mutate(self, info, id, **kwargs):
        artist = Artist.objects.get(pk=id)
        for key, value in kwargs.items():
            setattr(artist, key, value)
        artist.save()
        return UpdateArtist(artist=artist)

# ==== EVENT SERIES ====

class CreateEventSeries(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    event_series = graphene.Field(lambda: EventSeriesType)

    def mutate(self, info, name, **kwargs):
        obj = EventSeries(name=name, **kwargs)
        obj.save()
        return CreateEventSeries(event_series=obj)

class UpdateEventSeries(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    event_series = graphene.Field(lambda: EventSeriesType)

    def mutate(self, info, id, **kwargs):
        obj = EventSeries.objects.get(pk=id)
        for key, value in kwargs.items():
            setattr(obj, key, value)
        obj.save()
        return UpdateEventSeries(event_series=obj)

# ==== EVENT ====

class CreateEvent(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        date = graphene.Date(required=True)

    event = graphene.Field(lambda: EventType)

    def mutate(self, info, name, date, **kwargs):
        series_id = kwargs.pop("series_id", None)
        series = EventSeries.objects.get(pk=series_id) if series_id else None
        event = Event(name=name, date=date, series=series, **kwargs)
        event.save()
        return CreateEvent(event=event)

class UpdateEvent(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    event = graphene.Field(lambda: EventType)

    def mutate(self, info, id, **kwargs):
        event = Event.objects.get(pk=id)
        series_id = kwargs.pop("series_id", None)
        if series_id:
            event.series = EventSeries.objects.get(pk=series_id)
        for key, value in kwargs.items():
            setattr(event, key, value)
        event.save()
        return UpdateEvent(event=event)


# ==== REVIEW ====

class CreateReview(graphene.Mutation):
    class Arguments:
        stars = graphene.Decimal(required=True)
        user_id = graphene.ID(required=True)
        content_type_id = graphene.Int(required=True)
        object_id = graphene.Int(required=True)

    review = graphene.Field(lambda: ReviewType)

    def mutate(self, info, stars, user_id, content_type_id, object_id, **kwargs):
        user = User.objects.get(pk=user_id)
        review = Review(
            stars=stars,
            user=user,
            content_type_id=content_type_id,
            object_id=object_id,
            **kwargs
        )
        review.save()
        return CreateReview(review=review)

class UpdateReview(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    review = graphene.Field(lambda: ReviewType)

    def mutate(self, info, id, **kwargs):
        review = Review.objects.get(pk=id)
        for key, value in kwargs.items():
            setattr(review, key, value)
        review.save()
        return UpdateReview(review=review)

# ==== SUBREVIEW ====

class CreateSubReview(graphene.Mutation):
    class Arguments:
        review_id = graphene.ID(required=True)
        topic = graphene.String(required=True)
        stars = graphene.Decimal(required=True)

    subreview = graphene.Field(lambda: SubReviewType)

    def mutate(self, info, review_id, topic, stars, **kwargs):
        review = Review.objects.get(pk=review_id)
        obj = SubReview(review=review, topic=topic, stars=stars, **kwargs)
        obj.save()
        return CreateSubReview(subreview=obj)

class UpdateSubReview(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    subreview = graphene.Field(lambda: SubReviewType)

    def mutate(self, info, id, **kwargs):
        obj = SubReview.objects.get(pk=id)
        for key, value in kwargs.items():
            setattr(obj, key, value)
        obj.save()
        return UpdateSubReview(subreview=obj)

# ==== COVER ====

class CreateCover(graphene.Mutation):
    class Arguments:
        image = graphene.String(required=True)
        content_type_id = graphene.Int(required=True)
        object_id = graphene.Int(required=True)

    cover = graphene.Field(lambda: CoverType)

    def mutate(self, info, image, content_type_id, object_id, **kwargs):
        obj = Cover(image=image, content_type_id=content_type_id, object_id=object_id, **kwargs)
        obj.save()
        return CreateCover(cover=obj)

class UpdateCover(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    cover = graphene.Field(lambda: CoverType)

    def mutate(self, info, id, **kwargs):
        obj = Cover.objects.get(pk=id)
        for key, value in kwargs.items():
            setattr(obj, key, value)
        obj.save()
        return UpdateCover(cover=obj)

# ==== MUSIC VIDEO ====

class CreateMusicVideo(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        releaseDate = graphene.Date(required=True)
        youtubeURL = graphene.String(required=True)
        thumbnail = graphene.String(required=True)
        song_ids = graphene.List(graphene.ID)

    music_video = graphene.Field(lambda: MusicVideoType)

    def mutate(self, info, title, releaseDate, youtubeURL, thumbnail, song_ids=None, **kwargs):
        mv = MusicVideo(title=title, releaseDate=releaseDate, youtubeURL=youtubeURL, thumbnail=thumbnail, **kwargs)
        mv.save()
        if song_ids:
            mv.songs.set(Song.objects.filter(pk__in=song_ids))
        return CreateMusicVideo(music_video=mv)

class UpdateMusicVideo(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        song_ids = graphene.List(graphene.ID)
        add_songs_ids = graphene.List(graphene.ID)
        remove_songs_ids = graphene.List(graphene.ID)

    music_video = graphene.Field(lambda: MusicVideoType)

    def mutate(self, info, id, song_ids=None, add_songs_ids=None, remove_songs_ids=None, **kwargs):
        mv = MusicVideo.objects.get(pk=id)
        for key, value in kwargs.items():
            setattr(mv, key, value)

        if song_ids is not None:
            mv.songs.set(Song.objects.filter(pk__in=song_ids))

        if add_songs_ids is not None:
            to_add = Song.objects.filter(pk__in=add_songs_ids)
            mv.songs.add(*to_add)

        if remove_songs_ids is not None:
            to_remove = Song.objects.filter(pk__in=remove_songs_ids)
            mv.songs.remove(*to_remove)

        mv.save()
        return UpdateMusicVideo(music_video=mv)

# ==== SONG ====

class CreateSong(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        length = graphene.Int(required=True)
        release_date = graphene.Date(required=True)
        alternative_versions_ids = graphene.List(graphene.ID)

    song = graphene.Field(lambda: SongType)

    def mutate(self, info, title, length, release_date, alternative_versions_ids=None, **kwargs):
        song = Song(title=title, length=length, release_date=release_date, **kwargs)
        song.save()

        if alternative_versions_ids:
            related_songs = Song.objects.filter(id__in=alternative_versions_ids)
            song.alternative_versions.set(related_songs)

        return CreateSong(song=song)

class UpdateSong(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        alternative_versions_ids = graphene.List(graphene.ID)
        add_alternatives_ids = graphene.List(graphene.ID)
        remove_alternatives_ids = graphene.List(graphene.ID)

    song = graphene.Field(lambda: SongType)

    def mutate(self, info, id, alternative_versions_ids=None, add_alternatives_ids=None, remove_alternatives_ids=None, **kwargs):
        song = Song.objects.get(pk=id)
        for key, value in kwargs.items():
            setattr(song, key, value)

        if alternative_versions_ids:
            related_songs = Song.objects.filter(id__in=alternative_versions_ids)
            song.alternative_versions.set(related_songs)

        if add_alternatives_ids:
            to_add = Song.objects.filter(id__in=add_alternatives_ids)
            song.alternative_versions.add(*to_add)

        if remove_alternatives_ids:
            to_remove = Song.objects.filter(id__in=remove_alternatives_ids)
            song.alternative_versions.remove(*to_remove)

        song.save()
        return UpdateSong(song=song)

# ==== PROJECT ====

class ProjectTypeEnum(graphene.Enum):
    ALBUM = 'album'
    EP = 'ep'
    MIXTAPE = 'mixtape'
    SINGLE = 'single'

    @property
    def description(self):
        return {
            'ALBUM': 'An album',
            'EP': 'An EP',
            'MIXTAPE': 'A mixtape',
            'SINGLE': 'A single',
        }.get(self.name, '')

class CreateProject(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        number_of_songs = graphene.Int(required=True)
        release_date = graphene.Date(required=True)
        type = ProjectTypeEnum(required=True)
        length = graphene.Int(required=True)
        alternative_versions_ids = graphene.List(graphene.ID)

    project = graphene.Field(lambda: ProjectType)

    def mutate(self, info, alternative_versions_ids=None, **kwargs):
        project = Project(**kwargs)
        project.save()

        if alternative_versions_ids:
            related_projects = Project.objects.filter(id__in=alternative_versions_ids)
            project.alternative_versions.set(related_projects)

        return CreateProject(project=project)

class UpdateProject(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        alternative_versions_ids = graphene.List(graphene.ID)  # full replace
        add_alternatives_ids = graphene.List(graphene.ID)  # additive
        remove_alternatives_ids = graphene.List(graphene.ID)  # subtractive

    project = graphene.Field(lambda: ProjectType)

    def mutate(self, info, id, alternative_versions_ids = None, add_alternatives_ids = None, remove_alternatives_ids = None, **kwargs):
        project = Project.objects.get(pk=id)
        for key, value in kwargs.items():
            setattr(project, key, value)
        project.save()

        if alternative_versions_ids:
            projects = Project.objects.filter(id__in=alternative_versions_ids)
            project.alternative_versions.set(projects)

            # Add if specified
        if add_alternatives_ids:
            to_add = Project.objects.filter(id__in=add_alternatives_ids)
            project.alternative_versions.add(*to_add)

            # Remove if specified
        if remove_alternatives_ids:
            to_remove = Project.objects.filter(id__in=remove_alternatives_ids)
            project.alternative_versions.remove(*to_remove)

        return UpdateProject(project=project)

# ==== PODCAST ====

class CreatePodcast(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        since = graphene.Date(required=True)
        host_ids = graphene.List(graphene.ID)

    podcast = graphene.Field(lambda: PodcastType)

    def mutate(self, info, title, since, host_ids=None, **kwargs):
        podcast = Podcast(title=title, since=since, **kwargs)
        podcast.save()

        if host_ids:
            podcast.hosts.set(Artist.objects.filter(pk__in=host_ids))

        return CreatePodcast(podcast=podcast)

class UpdatePodcast(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        host_ids = graphene.List(graphene.ID)
        add_hosts_ids = graphene.List(graphene.ID)
        remove_hosts_ids = graphene.List(graphene.ID)

    podcast = graphene.Field(lambda: PodcastType)

    def mutate(self, info, id, host_ids=None, add_host_ids=None, remove_host_ids=None, **kwargs):
        podcast = Podcast.objects.get(pk=id)
        for key, value in kwargs.items():
            setattr(podcast, key, value)

        if host_ids is not None:
            podcast.hosts.set(Artist.objects.filter(pk__in=host_ids))

        if add_host_ids is not None:
            podcast.hosts.add(*Artist.objects.filter(pk__in=add_host_ids))

        if remove_host_ids is not None:
            podcast.hosts.remove(*Artist.objects.filter(pk__in=remove_host_ids))

        podcast.save()
        return UpdatePodcast(podcast=podcast)

# ==== OUTFIT ====

class CreateOutfit(graphene.Mutation):
    class Arguments:
        artist_id = graphene.ID()
        date = graphene.Date(required=True)
        preview_picture = graphene.String(required=True)
        instagram_post = graphene.String(required=True)
        matches_ids = graphene.List(graphene.ID)
        events_ids = graphene.List(graphene.ID)
        music_videos_ids = graphene.List(graphene.ID)
        covers_ids = graphene.List(graphene.ID)

    outfit = graphene.Field(lambda: OutfitType)

    def mutate(self, info, date, preview_picture, instagram_post, artist_id=None, matches_ids=None, events_ids=None, music_videos_ids=None, covers_ids=None, **kwargs):
        artist = Artist.objects.get(pk=artist_id) if artist_id else None
        outfit = Outfit(artist=artist, date=date, preview_picture=preview_picture, instagram_post=instagram_post, **kwargs)
        outfit.save()

        if matches_ids:
            outfit.matches.set(Outfit.objects.filter(pk__in=matches_ids))

        if events_ids:
            outfit.events.set(Event.objects.filter(pk__in=events_ids))

        if music_videos_ids:
            outfit.music_videos.set(MusicVideo.objects.filter(pk__in=music_videos_ids))

        if covers_ids:
            outfit.covers.set(Cover.objects.filter(pk__in=covers_ids))

        return CreateOutfit(outfit=outfit)

class UpdateOutfit(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        artist_id = graphene.ID()
        matches_ids = graphene.List(graphene.ID)
        add_matches_ids = graphene.List(graphene.ID)
        remove_matches_ids = graphene.List(graphene.ID)
        events_ids = graphene.List(graphene.ID)
        add_events_ids = graphene.List(graphene.ID)
        remove_events_ids = graphene.List(graphene.ID)
        music_videos_ids = graphene.List(graphene.ID)
        add_music_videos_ids = graphene.List(graphene.ID)
        remove_music_videos_ids = graphene.List(graphene.ID)
        covers_ids = graphene.List(graphene.ID)
        add_covers_ids = graphene.List(graphene.ID)
        remove_covers_ids = graphene.List(graphene.ID)

    outfit = graphene.Field(lambda: OutfitType)

    def mutate(self, info, id, artist_id=None, matches_ids=None, add_matches_ids=None, remove_matches_ids=None, events_ids=None, add_events_ids=None, remove_events_ids=None, music_videos_ids=None, add_music_videos_ids=None, remove_music_videos_ids=None, covers_ids=None, add_covers_ids=None, remove_covers_ids=None, **kwargs):
        outfit = Outfit.objects.get(pk=id)
        if artist_id:
            outfit.artist = Artist.objects.get(pk=artist_id)
        for key, value in kwargs.items():
            setattr(outfit, key, value)

        if matches_ids:
            outfit.matches.set(Outfit.objects.filter(pk__in=matches_ids))

        if add_matches_ids:
            outfit.matches.add(*Outfit.objects.filter(pk__in=add_matches_ids))

        if remove_matches_ids:
            outfit.matches.remove(*Outfit.objects.filter(pk__in=remove_matches_ids))

        if events_ids:
            outfit.events.set(Event.objects.filter(pk__in=events_ids))

        if add_events_ids:
            outfit.events.add(*Event.objects.filter(pk__in=add_events_ids))

        if remove_events_ids:
            outfit.events.remove(*Event.objects.filter(pk__in=remove_events_ids))

        if music_videos_ids:
            outfit.music_videos.set(MusicVideo.objects.filter(pk__in=music_videos_ids))

        if add_music_videos_ids:
            outfit.music_videos.add(*MusicVideo.objects.filter(pk__in=add_music_videos_ids))

        if remove_music_videos_ids:
            outfit.music_videos.remove(*MusicVideo.objects.filter(pk__in=remove_music_videos_ids))

        if covers_ids:
            outfit.covers.set(Cover.objects.filter(pk__in=covers_ids))

        if add_covers_ids:
            outfit.covers.add(*Cover.objects.filter(pk__in=add_covers_ids))

        if remove_covers_ids:
            outfit.covers.remove(*Cover.objects.filter(pk__in=remove_covers_ids))

        outfit.save()
        return UpdateOutfit(outfit=outfit)

# ==== PROFILE ====

class CreateProfile(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)

    profile = graphene.Field(lambda: ProfileType)

    def mutate(self, info, user_id, **kwargs):
        user = User.objects.get(pk=user_id)
        profile = Profile(user=user, **kwargs)
        profile.save()
        return CreateProfile(profile=profile)

class UpdateProfile(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

        # Profile fields
        hasPremium = graphene.Boolean()
        bannerPicture = graphene.String()
        profilePicture = graphene.String()
        bio = graphene.String()
        pronouns = graphene.String()
        accentColorHex = graphene.String()

        # User fields
        username = graphene.String()
        email = graphene.String()
        first_name = graphene.String()
        last_name = graphene.String()
        password = graphene.String()

        # Follow/unfollow
        add_following_ids = graphene.List(graphene.ID)
        remove_following_ids = graphene.List(graphene.ID)

    profile = graphene.Field(ProfileType)

    def mutate(self, info, id, add_following_ids=None, remove_following_ids=None, **kwargs):
        profile = Profile.objects.get(pk=id)
        user = profile.user

        # Update user fields
        user_fields = ["username", "email", "first_name", "last_name", "password"]
        for field in user_fields:
            if field in kwargs:
                value = kwargs.pop(field)
                if field == "password":
                    user.set_password(value)
                else:
                    setattr(user, field, value)
        user.save()

        # Update profile fields
        for key, value in kwargs.items():
            setattr(profile, key, value)

        # Handle following changes
        if add_following_ids:
            profile.following.add(*Profile.objects.filter(pk__in=add_following_ids))

        if remove_following_ids:
            profile.following.remove(*Profile.objects.filter(pk__in=remove_following_ids))

        profile.save()
        return UpdateProfile(profile=profile)

schema = graphene.Schema(query=Query)

# ==== SONG ARTIST ====

class CreateSongArtist(graphene.Mutation):
    class Arguments:
        song_id = graphene.ID(required=True)
        artist_id = graphene.ID(required=True)
        position = graphene.Int(required=True)

    song_artist = graphene.Field(lambda: SongArtistType)

    def mutate(self, info, song_id, artist_id, position):
        song = Song.objects.get(pk=song_id)
        artist = Artist.objects.get(pk=artist_id)
        song_artist = SongArtist(song=song, artist=artist, position=position)
        song_artist.save()
        return CreateSongArtist(song_artist=song_artist)

class UpdateSongArtist(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    song_artist = graphene.Field(lambda: SongArtistType)

    def mutate(self, info, id, **kwargs):
        song_artist = SongArtist.objects.get(pk=id)
        for key, value in kwargs.items():
            setattr(song_artist, key, value)
        song_artist.save()
        return UpdateSongArtist(song_artist=song_artist)


# ==== PROJECT ARTIST ====

class CreateProjectArtist(graphene.Mutation):
    class Arguments:
        project_id = graphene.ID(required=True)
        artist_id = graphene.ID(required=True)
        position = graphene.Int(required=True)

    project_artist = graphene.Field(lambda: ProjectArtistType)

    def mutate(self, info, project_id, artist_id, position):
        project = Project.objects.get(pk=project_id)
        artist = Artist.objects.get(pk=artist_id)
        project_artist = ProjectArtist(project=project, artist=artist, position=position)
        project_artist.save()
        return CreateProjectArtist(project_artist=project_artist)

class UpdateProjectArtist(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    project_artist = graphene.Field(lambda: ProjectArtistType)

    def mutate(self, info, id, **kwargs):
        project_artist = ProjectArtist.objects.get(pk=id)
        for key, value in kwargs.items():
            setattr(project_artist, key, value)
        project_artist.save()
        return UpdateProjectArtist(project_artist=project_artist)


# ==== PROJECT SONG ====

class CreateProjectSong(graphene.Mutation):
    class Arguments:
        project_id = graphene.ID(required=True)
        song_id = graphene.ID(required=True)
        position = graphene.Int(required=True)

    project_song = graphene.Field(lambda: ProjectSongType)

    def mutate(self, info, project_id, song_id, position):
        project = Project.objects.get(pk=project_id)
        song = Song.objects.get(pk=song_id)
        project_song = ProjectSong(project=project, song=song, position=position)
        project_song.save()
        return CreateProjectSong(project_song=project_song)

class UpdateProjectSong(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    project_song = graphene.Field(lambda: ProjectSongType)

    def mutate(self, info, id, **kwargs):
        project_song = ProjectSong.objects.get(pk=id)
        for key, value in kwargs.items():
            setattr(project_song, key, value)
        project_song.save()
        return UpdateProjectSong(project_song=project_song)


# ==== CONVERSATION ====

class CreateConversation(graphene.Mutation):
    class Arguments:
        participant_ids = graphene.List(graphene.ID)

    conversation = graphene.Field(lambda: ConversationType)

    def mutate(self, info, participants_ids):
        conversation = Conversation()
        conversation.save()
        if participants_ids:
            conversation.participants.set(User.objects.filter(pk__in=participants_ids))

            # ADD THESE LINES - trigger conversation_updated subscription
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "conversations_updates",
                {
                    "type": "conversation_updated",
                    "conversation_id": conversation.id
                }
            )

            # Send to user-specific groups for each participant
            if participants_ids:
                for participant_id in participants_ids:
                    async_to_sync(channel_layer.group_send)(
                        f"conversations_updates_{participant_id}",
                        {
                            "type": "conversation_updated",
                            "conversation_id": conversation.id
                        }
                    )


        return CreateConversation(conversation=conversation, latest_message=None, latest_message_time=None, latest_message_text=None, latest_message_sender=None)

class UpdateConversation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        latest_message_id = graphene.ID(required=True)
        latest_message_time = graphene.DateTime(required=True)
        latest_message_text = graphene.String(required=True)
        latest_message_sender_id = graphene.ID(required=True)

    conversation = graphene.Field(lambda: ConversationType)

    def mutate(self, info, id, latest_message_id, latest_message_time, latest_message_text, latest_message_sender_id):
        conversation = Conversation.objects.get(pk=id)
        latest_message = Message.objects.get(pk=latest_message_id)
        latest_message_sender = User.objects.get(pk=latest_message_sender_id)
        conversation.latest_message = latest_message
        conversation.latest_message_time = latest_message_time
        conversation.latest_message_text = latest_message_text
        conversation.latest_message_sender = latest_message_sender
        conversation.save()

        # ADD THESE LINES - trigger conversation_updated subscription
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "conversations_updates",
            {
                "type": "conversation_updated",
                "conversation_id": conversation.id
            }
        )

        # Send to user-specific groups for each participant
        for participant in conversation.participants.all():
            async_to_sync(channel_layer.group_send)(
                f"conversations_updates_{participant.id}",
                {
                    "type": "conversation_updated",
                    "conversation_id": conversation.id
                }
            )

        return UpdateConversation(conversation=conversation)


# ==== MESSAGE ====


class CreateMessage(graphene.Mutation):
    class Arguments:
        conversation_id = graphene.ID(required=True)
        text = graphene.String(required=True)
        sender_id = graphene.ID(required=True)
        replying_to_message_id = graphene.ID()

    message = graphene.Field(lambda: MessageType)

    def mutate(self, info, conversation_id, text, sender_id, replying_to_message_id=None):
        conversation = Conversation.objects.get(pk=conversation_id)
        sender = User.objects.get(pk=sender_id)
        replying_to_message = Message.objects.get(pk=replying_to_message_id) if replying_to_message_id else None
        message = Message(conversation=conversation, text=text, sender=sender, replying_to=replying_to_message)
        message.save()

        # ADD THESE LINES - trigger subscriptions
        channel_layer = get_channel_layer()

        # Trigger message_created subscription
        async_to_sync(channel_layer.group_send)(
            "messages_updates",
            {
                "type": "message_created",
                "message_id": message.id,
                "conversation_id": conversation.id
            }
        )

        # Also send to conversation-specific group
        async_to_sync(channel_layer.group_send)(
            f"messages_updates_{conversation.id}",
            {
                "type": "message_created",
                "message_id": message.id,
                "conversation_id": conversation.id
            }
        )

        return CreateMessage(message=message)


class UpdateMessage(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        add_liked_by_ids = graphene.List(graphene.ID)
        remove_liked_by_ids = graphene.List(graphene.ID)

    message = graphene.Field(lambda: MessageType)

    def mutate(self, info, id, add_liked_by_ids=None, remove_liked_by_ids=None,**kwargs):
        message = Message.objects.get(pk=id)
        for key, value in kwargs.items():
            setattr(message, key, value)

        if add_liked_by_ids:
            message.liked_by.add(*User.objects.filter(pk__in=add_liked_by_ids))

        if remove_liked_by_ids:
            message.liked_by.remove(*User.objects.filter(pk__in=remove_liked_by_ids))

        message.save()

        # ADD THESE LINES - trigger message_updated subscription
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "messages_updates",
            {
                "type": "message_updated",
                "message_id": message.id,
                "conversation_id": message.conversation.id
            }
        )

        # Also send to conversation-specific group
        async_to_sync(channel_layer.group_send)(
            f"messages_updates_{message.conversation.id}",
            {
                "type": "message_updated",
                "message_id": message.id,
                "conversation_id": message.conversation.id
            }
        )

        return UpdateMessage(message=message)

# ==== DELETES ====


class DeleteArtist(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    ok = graphene.Boolean()
    def mutate(self, info, id):
        Artist.objects.get(pk=id).delete()
        return DeleteArtist(ok=True)

class DeleteEventSeries(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    ok = graphene.Boolean()
    def mutate(self, info, id):
        EventSeries.objects.get(pk=id).delete()
        return DeleteEventSeries(ok=True)

class DeleteEvent(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    ok = graphene.Boolean()
    def mutate(self, info, id):
        Event.objects.get(pk=id).delete()
        return DeleteEvent(ok=True)

class DeleteReview(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        try:
            review = Review.objects.get(pk=id)
            content_object = review.content_object

            # Use current values
            old_count = content_object.reviews_count
            old_avg = content_object.star_average
            deleted_stars = float(review.stars)

            # Delete review (will cascade subreviews too)
            review.delete()

            # Efficient recalculation
            new_count = old_count - 1
            if new_count <= 0:
                new_avg = 0.0
            else:
                new_avg = ((old_avg * old_count) - deleted_stars) / new_count

            content_object.reviews_count = new_count
            content_object.star_average = new_avg
            content_object.save()

            return DeleteReview(ok=True)
        except Review.DoesNotExist:
            return DeleteReview(ok=False)

class DeleteSubReview(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    ok = graphene.Boolean()
    def mutate(self, info, id):
        SubReview.objects.get(pk=id).delete()
        return DeleteSubReview(ok=True)

class DeleteCover(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        cover = Cover.objects.get(pk=id)

        # Delete all associated reviews first
        cover.reviews.all().delete()

        # Now delete the cover
        cover.delete()

        return DeleteCover(ok=True)

class DeleteMusicVideo(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    ok = graphene.Boolean()
    def mutate(self, info, id):
        MusicVideo.objects.get(pk=id).delete()
        return DeleteMusicVideo(ok=True)

class DeleteSong(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    ok = graphene.Boolean()
    def mutate(self, info, id):
        song = Song.objects.get(pk=id)

        # Delete related SongArtist objects
        song.songartist_set.all().delete()
        # Delete related ProjectSong objects (song may be part of projects)
        song.projectsong_set.all().delete()

        song.delete()
        return DeleteSong(ok=True)

class DeleteSongArtist(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    ok = graphene.Boolean()
    def mutate(self, info, id):
        SongArtist.objects.get(pk=id).delete()
        return DeleteSongArtist(ok=True)

class DeleteProject(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    ok = graphene.Boolean()
    def mutate(self, info, id):
        project = Project.objects.get(pk=id)

        # Delete related ProjectArtist objects
        project.projectartist_set.all().delete()
        # Delete related ProjectSong objects
        project.projectsong_set.all().delete()
        # Clean up many-to-many references (especially self-referencing ones)
        project.alternative_versions.clear()
        # Delete related Cover objects
        project.covers.all().delete()

        project.delete()
        return DeleteProject(ok=True)

class DeleteProjectArtist(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    ok = graphene.Boolean()
    def mutate(self, info, id):
        ProjectArtist.objects.get(pk=id).delete()
        return DeleteProjectArtist(ok=True)

class DeleteProjectSong(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    ok = graphene.Boolean()
    def mutate(self, info, id):
        ProjectSong.objects.get(pk=id).delete()
        return DeleteProjectSong(ok=True)

class DeletePodcast(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    ok = graphene.Boolean()
    def mutate(self, info, id):
        podcast = Podcast.objects.get(pk=id)

        podcast.covers.all().delete()

        podcast.delete()
        return DeletePodcast(ok=True)

class DeleteOutfit(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    ok = graphene.Boolean()
    def mutate(self, info, id):
        outfit = Outfit.objects.get(pk=id)
        # Clear self-referencing many-to-many
        outfit.matches.clear()
        outfit.delete()
        return DeleteOutfit(ok=True)

class DeleteConversation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    ok = graphene.Boolean()
    def mutate(self, info, id):
        conversation = Conversation.objects.get(pk=id)

        # Get participants before deletion for subscription notification
        participant_ids = list(conversation.participants.values_list('id', flat=True))

        conversation.delete()

        # ADD THESE LINES - trigger conversation deletion notification
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "conversations_updates",
            {
                "type": "conversation_deleted",
                "conversation_id": int(id)
            }
        )

        # Send to user-specific groups for each participant
        for participant_id in participant_ids:
            async_to_sync(channel_layer.group_send)(
                f"conversations_updates_{participant_id}",
                {
                    "type": "conversation_deleted",
                    "conversation_id": int(id)
                }
            )

        return DeleteConversation(ok=True)

class DeleteMessage(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    ok = graphene.Boolean()
    def mutate(self, info, id):
        message = Message.objects.get(pk=id)
        conversation_id = message.conversation.id

        message.delete()

        # ADD THESE LINES - trigger message deletion notification
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "messages_updates",
            {
                "type": "message_deleted",
                "message_id": int(id),
                "conversation_id": conversation_id
            }
        )

        # Also send to conversation-specific group
        async_to_sync(channel_layer.group_send)(
            f"messages_updates_{conversation_id}",
            {
                "type": "message_deleted",
                "message_id": int(id),
                "conversation_id": conversation_id
            }
        )

        return DeleteMessage(ok=True)

class DeleteProfile(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        profile = Profile.objects.get(pk=id)

        # Decrement followersCount/followingCount of related users
        for follower in profile.followers.all():
            follower.followingCount -= 1
            follower.save()

        for following in profile.following.all():
            following.followersCount -= 1
            following.save()

        user = profile.user
        profile.delete()
        user.delete()

        return DeleteProfile(ok=True)

class Mutation(graphene.ObjectType):
    create_artist = CreateArtist.Field()
    update_artist = UpdateArtist.Field()
    delete_artist = DeleteArtist.Field()

    create_project = CreateProject.Field()
    update_project = UpdateProject.Field()
    delete_project = DeleteProject.Field()

    create_project_artist = CreateProjectArtist.Field()
    update_project_artist = UpdateProjectArtist.Field()
    delete_project_artist = DeleteProjectArtist.Field()

    create_project_song = CreateProjectSong.Field()
    update_project_song = UpdateProjectSong.Field()
    delete_project_song = DeleteProjectSong.Field()

    create_event_series = CreateEventSeries.Field()
    update_event_series = UpdateEventSeries.Field()
    delete_event_series = DeleteEventSeries.Field()

    create_event = CreateEvent.Field()
    update_event = UpdateEvent.Field()
    delete_event = DeleteEvent.Field()

    create_review = CreateReview.Field()
    update_review = UpdateReview.Field()
    delete_review = DeleteReview.Field()

    create_subreview = CreateSubReview.Field()
    update_subreview = UpdateSubReview.Field()
    delete_subreview = DeleteSubReview.Field()

    create_cover = CreateCover.Field()
    update_cover = UpdateCover.Field()
    delete_cover = DeleteCover.Field()

    create_music_video = CreateMusicVideo.Field()
    update_music_video = UpdateMusicVideo.Field()
    delete_music_video = DeleteMusicVideo.Field()

    create_song = CreateSong.Field()
    update_song = UpdateSong.Field()
    delete_song = DeleteSong.Field()

    create_song_artist = CreateSongArtist.Field()
    update_song_artist = UpdateSongArtist.Field()
    delete_song_artist = DeleteSongArtist.Field()

    create_conversation = CreateConversation.Field()
    update_conversation = UpdateConversation.Field()
    delete_conversation = DeleteConversation.Field()

    create_message = CreateMessage.Field()
    update_message = UpdateMessage.Field()
    delete_message = DeleteMessage.Field()

    create_profile = CreateProfile.Field()
    update_profile = UpdateProfile.Field()
    delete_profile = DeleteProfile.Field()

    create_outfit = CreateOutfit.Field()
    update_outfit = UpdateOutfit.Field()
    delete_outfit = DeleteOutfit.Field()

    create_podcast = CreatePodcast.Field()
    update_podcast = UpdatePodcast.Field()
    delete_podcast = DeletePodcast.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
'''