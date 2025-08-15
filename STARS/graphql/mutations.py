import strawberry
import strawberry_django
from strawberry import auto
from typing import List, Optional
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.db.models import Count
from strawberry.types import Info
from django.contrib.auth import password_validation, login, authenticate, logout
from django.core.exceptions import ValidationError
from django.db import transaction
import enum


# --- IMPORTS FOR SOCIAL LOGIN ---
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialApp, SocialLogin, SocialToken

from STARS import models
from . import types


# -----------------------------------------------------------------------------
# Input Types
# -----------------------------------------------------------------------------

@strawberry_django.input(models.Artist)
class ArtistCreateInput:
    name: auto
    picture: auto
    bio: Optional[str] = None
    wikipedia: Optional[str] = None
    pronouns: Optional[str] = None
    birthdate: Optional[str] = None
    origin: Optional[str] = None
    website: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None
    youtube_channel: Optional[str] = None
    spotify: Optional[str] = None
    apple_music: Optional[str] = None
    youtube_music: Optional[str] = None
    tidal: Optional[str] = None
    deezer: Optional[str] = None
    soundcloud: Optional[str] = None
    bandcamp: Optional[str] = None
    is_featured: Optional[bool] = False
    featured_message: Optional[str] = None


@strawberry.input
class ArtistUpdateInput:
    id: strawberry.ID
    name: Optional[str] = strawberry.UNSET
    picture: Optional[str] = strawberry.UNSET
    bio: Optional[str] = strawberry.UNSET
    wikipedia: Optional[str] = strawberry.UNSET
    pronouns: Optional[str] = strawberry.UNSET
    birthdate: Optional[str] = strawberry.UNSET
    origin: Optional[str] = strawberry.UNSET
    website: Optional[str] = strawberry.UNSET
    facebook: Optional[str] = strawberry.UNSET
    instagram: Optional[str] = strawberry.UNSET
    twitter: Optional[str] = strawberry.UNSET
    youtube_channel: Optional[str] = strawberry.UNSET
    spotify: Optional[str] = strawberry.UNSET
    apple_music: Optional[str] = strawberry.UNSET
    youtube_music: Optional[str] = strawberry.UNSET
    tidal: Optional[str] = strawberry.UNSET
    deezer: Optional[str] = strawberry.UNSET
    soundcloud: Optional[str] = strawberry.UNSET
    bandcamp: Optional[str] = strawberry.UNSET
    is_featured: Optional[bool] = strawberry.UNSET
    featured_message: Optional[str] = strawberry.UNSET


@strawberry_django.input(models.EventSeries)
class EventSeriesCreateInput:
    name: auto
    description: Optional[str] = None
    is_featured: Optional[bool] = False
    featured_message: Optional[str] = None


@strawberry.input
class EventSeriesUpdateInput:
    id: strawberry.ID
    name: Optional[str] = strawberry.UNSET
    description: Optional[str] = strawberry.UNSET
    is_featured: Optional[bool] = strawberry.UNSET
    featured_message: Optional[str] = strawberry.UNSET


@strawberry_django.input(models.Event)
class EventCreateInput:
    name: auto
    date: auto
    location: Optional[str] = None
    is_one_time: Optional[bool] = False
    series_id: Optional[strawberry.ID] = None
    is_featured: Optional[bool] = False
    featured_message: Optional[str] = None


@strawberry.input
class EventUpdateInput:
    id: strawberry.ID
    name: Optional[str] = strawberry.UNSET
    date: Optional[str] = strawberry.UNSET
    location: Optional[str] = strawberry.UNSET
    is_one_time: Optional[bool] = strawberry.UNSET
    series_id: Optional[strawberry.ID] = strawberry.UNSET
    is_featured: Optional[bool] = strawberry.UNSET
    featured_message: Optional[str] = strawberry.UNSET



@strawberry_django.input(models.Comment)
class CommentCreateInput:
    review_id: strawberry.ID
    text: auto

@strawberry.input
class CommentUpdateInput:
    id: strawberry.ID
    text: Optional[str] = strawberry.UNSET


@strawberry.input
class ReviewDataInput:
    stars: float
    text: Optional[str] = None


@strawberry.input
class ReviewUpdateInput:
    id: strawberry.ID
    stars: Optional[float] = strawberry.UNSET
    text: Optional[str] = strawberry.UNSET
    is_latest: Optional[bool] = strawberry.UNSET


@strawberry.input
class SubReviewDataInput:
    topic: str
    stars: float
    text: Optional[str] = None


@strawberry.input
class SubReviewUpdateInput:
    id: strawberry.ID
    topic: Optional[str] = strawberry.UNSET
    text: Optional[str] = strawberry.UNSET
    stars: Optional[float] = strawberry.UNSET


@strawberry_django.input(models.MusicVideo)
class MusicVideoCreateInput:
    title: auto
    release_date: auto
    youtube: auto
    thumbnail: auto
    is_featured: Optional[bool] = False


@strawberry.input
class MusicVideoUpdateInput:
    id: strawberry.ID
    title: Optional[str] = strawberry.UNSET
    release_date: Optional[str] = strawberry.UNSET
    youtube: Optional[str] = strawberry.UNSET
    thumbnail: Optional[str] = strawberry.UNSET
    is_featured: Optional[bool] = strawberry.UNSET
    featured_message: Optional[str] = strawberry.UNSET



@strawberry_django.input(models.Song)
class SongCreateInput:
    title: auto
    length: auto
    release_date: auto
    preview: Optional[str] = None
    is_featured: Optional[bool] = False


@strawberry.input
class SongUpdateInput:
    id: strawberry.ID
    title: Optional[str] = strawberry.UNSET
    length: Optional[int] = strawberry.UNSET
    release_date: Optional[str] = strawberry.UNSET
    preview: Optional[str] = strawberry.UNSET
    is_featured: Optional[bool] = strawberry.UNSET
    featured_message: Optional[str] = strawberry.UNSET



@strawberry.input
class ProjectArtistInput:
    artist_id: strawberry.ID
    position: int

@strawberry.input
class ProjectSongInput:
    song_id: strawberry.ID
    position: int


@strawberry_django.input(models.Project)
class ProjectCreateInput:
    title: auto
    number_of_songs: auto
    release_date: auto
    project_type: auto
    length: auto
    spotify: Optional[str] = None
    apple_music: Optional[str] = None
    youtube_music: Optional[str] = None
    tidal: Optional[str] = None
    deezer: Optional[str] = None
    soundcloud: Optional[str] = None
    bandcamp: Optional[str] = None
    is_featured: Optional[bool] = False
    artists: Optional[List[ProjectArtistInput]] = None
    songs: Optional[List[ProjectSongInput]] = None


@strawberry.input
class ProjectUpdateInput:
    id: strawberry.ID
    title: Optional[str] = strawberry.UNSET
    number_of_songs: Optional[int] = strawberry.UNSET
    release_date: Optional[str] = strawberry.UNSET
    project_type: Optional[str] = strawberry.UNSET
    length: Optional[int] = strawberry.UNSET
    spotify: Optional[str] = strawberry.UNSET
    apple_music: Optional[str] = strawberry.UNSET
    youtube_music: Optional[str] = strawberry.UNSET
    tidal: Optional[str] = strawberry.UNSET
    deezer: Optional[str] = strawberry.UNSET
    soundcloud: Optional[str] = strawberry.UNSET
    bandcamp: Optional[str] = strawberry.UNSET
    is_featured: Optional[bool] = strawberry.UNSET
    featured_message: Optional[str] = strawberry.UNSET



@strawberry_django.input(models.Podcast)
class PodcastCreateInput:
    title: auto
    since: auto
    description: Optional[str] = None
    website: Optional[str] = None
    spotify: Optional[str] = None
    apple_podcasts: Optional[str] = None
    youtube: Optional[str] = None
    youtube_music: Optional[str] = None
    is_featured: Optional[bool] = False
    host_ids: Optional[List[strawberry.ID]] = None


@strawberry.input
class PodcastUpdateInput:
    id: strawberry.ID
    title: Optional[str] = strawberry.UNSET
    description: Optional[str] = strawberry.UNSET
    since: Optional[str] = strawberry.UNSET
    website: Optional[str] = strawberry.UNSET
    spotify: Optional[str] = strawberry.UNSET
    apple_podcasts: Optional[str] = strawberry.UNSET
    youtube: Optional[str] = strawberry.UNSET
    youtube_music: Optional[str] = strawberry.UNSET
    is_featured: Optional[bool] = strawberry.UNSET
    featured_message: Optional[str] = strawberry.UNSET



@strawberry_django.input(models.Outfit)
class OutfitCreateInput:
    artist_id: strawberry.ID
    date: auto
    preview_picture: auto
    instagram_post: auto
    description: Optional[str] = None
    is_featured: Optional[bool] = False


@strawberry.input
class OutfitUpdateInput:
    id: strawberry.ID
    artist_id: Optional[strawberry.ID] = strawberry.UNSET
    description: Optional[str] = strawberry.UNSET
    date: Optional[str] = strawberry.UNSET
    preview_picture: Optional[str] = strawberry.UNSET
    instagram_post: Optional[str] = strawberry.UNSET
    is_featured: Optional[bool] = strawberry.UNSET
    featured_message: Optional[str] = strawberry.UNSET



@strawberry.input
class ProfileUpdateInput:
    id: strawberry.ID
    bio: Optional[str] = strawberry.UNSET
    pronouns: Optional[str] = strawberry.UNSET
    banner_picture: Optional[str] = strawberry.UNSET
    profile_picture: Optional[str] = strawberry.UNSET
    accent_color_hex: Optional[str] = strawberry.UNSET


@strawberry.input
class SignupInput:
    email: str
    password: str
    password_confirmation: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@strawberry_django.input(models.SongArtist)
class SongArtistCreateInput:
    song_id: strawberry.ID
    artist_id: strawberry.ID
    position: auto


@strawberry_django.input(models.ProjectArtist)
class ProjectArtistCreateInput:
    project_id: strawberry.ID
    artist_id: strawberry.ID
    position: auto


@strawberry_django.input(models.ProjectSong)
class ProjectSongCreateInput:
    project_id: strawberry.ID
    song_id: strawberry.ID
    position: auto


@strawberry.input
class MessageDataInput:
    text: str


@strawberry.input
class CoverDataInput:
    image_url: str


@strawberry.input
class ConversationCreateInput:
    participant_ids: list[strawberry.ID]


@strawberry.input
class LoginInput:
    username: str
    password: str


@strawberry.type
class SuccessMessage:
    message: str


@strawberry.enum
class LikeAction(enum.Enum):
    LIKE = "like"
    UNLIKE = "unlike"
    DISLIKE = "dislike"
    UNDISLIKE = "undislike"


@strawberry.type
class Mutation:
    create_artist: types.Artist = strawberry_django.mutations.create(ArtistCreateInput)
    update_artist: types.Artist = strawberry_django.mutations.update(ArtistUpdateInput)
    delete_artist: types.Artist = strawberry_django.mutations.delete(strawberry.ID)

    update_project: types.Project = strawberry_django.mutations.update(ProjectUpdateInput)
    delete_project: types.Project = strawberry_django.mutations.delete(strawberry.ID)

    create_song: types.Song = strawberry_django.mutations.create(SongCreateInput)
    update_song: types.Song = strawberry_django.mutations.update(SongUpdateInput)
    delete_song: types.Song = strawberry_django.mutations.delete(strawberry.ID)

    create_event_series: types.EventSeries = strawberry_django.mutations.create(EventSeriesCreateInput)
    update_event_series: types.EventSeries = strawberry_django.mutations.update(EventSeriesUpdateInput)
    delete_event_series: types.EventSeries = strawberry_django.mutations.delete(strawberry.ID)

    update_event: types.Event = strawberry_django.mutations.update(EventUpdateInput)
    delete_event: types.Event = strawberry_django.mutations.delete(strawberry.ID)

    update_review: types.Review = strawberry_django.mutations.update(ReviewUpdateInput)
    delete_review: types.Review = strawberry_django.mutations.delete(strawberry.ID)
    update_subreview: types.SubReview = strawberry_django.mutations.update(SubReviewUpdateInput)
    delete_subreview: types.SubReview = strawberry_django.mutations.delete(strawberry.ID)

    create_music_video: types.MusicVideo = strawberry_django.mutations.create(MusicVideoCreateInput)
    update_music_video: types.MusicVideo = strawberry_django.mutations.update(MusicVideoUpdateInput)
    delete_music_video: types.MusicVideo = strawberry_django.mutations.delete(strawberry.ID)
    update_podcast: types.Podcast = strawberry_django.mutations.update(PodcastUpdateInput)
    delete_podcast: types.Podcast = strawberry_django.mutations.delete(strawberry.ID)
    create_outfit: types.Outfit = strawberry_django.mutations.create(OutfitCreateInput)
    update_outfit: types.Outfit = strawberry_django.mutations.update(OutfitUpdateInput)
    delete_outfit: types.Outfit = strawberry_django.mutations.delete(strawberry.ID)

    update_profile: types.Profile = strawberry_django.mutations.update(ProfileUpdateInput)

    update_comment: types.Comment = strawberry_django.mutations.update(CommentUpdateInput)
    delete_comment: types.Comment = strawberry_django.mutations.delete(strawberry.ID)


    @strawberry.mutation
    async def create_event(self, info: Info, data: EventCreateInput) -> types.Event:

        def _create_sync():
            if data.is_one_time:

                event = models.Event.objects.create(
                    name=data.name,
                    date=data.date,
                    location=data.location,
                    is_one_time=data.is_one_time,
                    event_series=None,
                    is_featured=data.is_featured,
                    featured_message=data.featured_message
                )

            else:
                event_series = models.EventSeries.objects.get(pk=data.series_id)

                event = models.Event.objects.create(
                    name = data.name,
                    date = data.date,
                    location = data.location,
                    is_one_time = data.is_one_time,
                    event_series = event_series,
                    is_featured = data.is_featured,
                    featured_message = data.featured_message
                )


            return event

        return await database_sync_to_async(_create_sync)()

    """
    @strawberry.mutation
    async def create_project(self, info: Info, data: ProjectCreateInput) -> types.Project:
        # (Add permission checks here if needed)

        def _create_sync():
            project_data = strawberry.asdict(data)

            # Separate the nested artists and songs data
            artist_inputs = project_data.pop("artists", None)
            song_inputs = project_data.pop("songs", None)

            with transaction.atomic():
                # Create the main project object
                project = models.Project.objects.create(**project_data)

                # If artists were provided, create the links
                if artist_inputs:
                    project_artists = [
                        models.ProjectArtist(
                            project=project,
                            artist_id=artist['artist_id'],
                            position=artist['position']
                        ) for artist in artist_inputs
                    ]
                    models.ProjectArtist.objects.bulk_create(project_artists)

                # If songs were provided, create the links
                if song_inputs:
                    project_songs = [
                        models.ProjectSong(
                            project=project,
                            song_id=song['song_id'],
                            position=song['position']
                        ) for song in song_inputs
                    ]
                    models.ProjectSong.objects.bulk_create(project_songs)

            return project

        return await database_sync_to_async(_create_sync)()
    """

    """
    @strawberry.mutation
    async def create_podcast(self, info: Info, data: PodcastCreateInput) -> types.Podcast:
        # (You would add permission checks here, e.g., if user is staff)

        def _create_sync():
            # Convert the input to a dictionary
            podcast_data = strawberry.asdict(data)
            # Separate the host_ids from the other data
            host_ids = podcast_data.pop("host_ids", None)

            # Use a transaction to ensure both steps succeed or fail together
            with transaction.atomic():
                # Create the podcast with the main data
                podcast = models.Podcast.objects.create(**podcast_data)

                # If host_ids were provided, find the artists and add them
                if host_ids:
                    hosts = models.Artist.objects.filter(pk__in=host_ids)
                    podcast.hosts.set(hosts)

            return podcast

        return await database_sync_to_async(_create_sync)()
    """

    @strawberry.mutation
    async def create_comment(self, info: Info, data: CommentCreateInput) -> types.Comment:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required.")

        def _create_sync():
            review = models.Review.objects.get(pk=data.review_id)

            comment = models.Comment.objects.create(
                review=review,
                user=user,
                text=data.text
            )
            return comment

        return await database_sync_to_async(_create_sync)()

    """
    @strawberry.mutation
    async def like_dislike_comment(self, info: Info, comment_id: strawberry.ID, action: LikeAction) -> types.Comment:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required.")

        def _update_sync():
            comment = models.Comment.objects.get(pk=comment_id)

            # Logic to handle likes and dislikes
            if action == LikeAction.LIKE:
                comment.liked_by.add(user)
                comment.disliked_by.remove(user)
            elif action == LikeAction.UNLIKE:
                comment.liked_by.remove(user)
            elif action == LikeAction.DISLIKE:
                comment.disliked_by.add(user)
                comment.liked_by.remove(user)
            elif action == LikeAction.UNDISLIKE:
                comment.disliked_by.remove(user)

            # Update counts and save
            comment.likes_count = comment.liked_by.count()
            comment.dislikes_count = comment.disliked_by.count()
            comment.save()
            return comment

        return await database_sync_to_async(_update_sync)()
    """

    """
    @strawberry.mutation
    async def like_dislike_review(self, info: Info, review_id: strawberry.ID, action: LikeAction) -> types.Review:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required.")

        def _update_sync():
            review = models.Review.objects.get(pk=review_id)

            if action == LikeAction.LIKE:
                review.liked_by.add(user)
                review.disliked_by.remove(user)
            elif action == LikeAction.UNLIKE:
                review.liked_by.remove(user)
            elif action == LikeAction.DISLIKE:
                review.disliked_by.add(user)
                review.liked_by.remove(user)
            elif action == LikeAction.UNDISLIKE:
                review.disliked_by.remove(user)

            review.likes_count = review.liked_by.count()
            review.dislikes_count = review.disliked_by.count()
            review.save()
            return review

        return await database_sync_to_async(_update_sync)()

    """

    """
    @strawberry.mutation
    async def add_hosts_to_podcast(self, info: Info, podcast_id: strawberry.ID,
                                   artist_ids: List[strawberry.ID]) -> types.Podcast:
        # You would add permission checks here (e.g., if user is staff)

        def _update_sync():
            podcast = models.Podcast.objects.get(pk=podcast_id)
            artists = models.Artist.objects.filter(pk__in=artist_ids)
            podcast.hosts.add(*artists)
            return podcast

        return await database_sync_to_async(_update_sync)()
    """

    """
    @strawberry.mutation
    async def login_user(self, info: Info, data: LoginInput) -> types.User:
        request = info.context.request

        # Define a synchronous inner function for all auth/database logic
        def _login_sync():
            username_or_email = data.username
            password = data.password
            user = None

            # Check if the input string contains '@' to see if it's an email
            if '@' in username_or_email:
                try:
                    # Find the user by their case-insensitive email
                    user_obj = User.objects.get(email__iexact=username_or_email)
                    # Now, authenticate using that user's actual username
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    # If the email doesn't exist, user will remain None, and auth will fail
                    pass
            else:
                # If no '@', assume it's a username and authenticate directly
                user = authenticate(request, username=username_or_email, password=password)

            if user is None:
                raise Exception("Invalid credentials.")

            # If authentication was successful, log the user in
            login(request, user)
            return user


        return await database_sync_to_async(_login_sync)()
    """

    """
    @strawberry.mutation
    async def logout_user(self, info: Info) -> SuccessMessage:
        request = info.context.request

        def _logout_sync():
            if not request.user.is_authenticated:
                return "User was already logged out."
            logout(request)
            return "Successfully logged out."

        message = await sync_to_async(_logout_sync)()
        return SuccessMessage(message=message)

    """

    """
    @strawberry.mutation
    async def signup(self, data: SignupInput) -> types.User:
        if data.password != data.password_confirmation:
            raise Exception("Passwords do not match.")

        user_exists = await database_sync_to_async(User.objects.filter(email=data.email).exists)()
        if user_exists:
            raise Exception("A user with this email already exists.")

        username_exists = await database_sync_to_async(User.objects.filter(username=data.username).exists)()
        if username_exists:
            raise Exception("A user with this username already exists.")

        try:
            await sync_to_async(password_validation.validate_password)(data.password)
        except ValidationError as e:
            raise Exception(f"Invalid password: {', '.join(e.messages)}")

        user = await database_sync_to_async(User.objects.create_user)(
            username=data.username,
            email=data.email,
            password=data.password,
            first_name=data.first_name or "",
            last_name=data.last_name or ""
        )
        await database_sync_to_async(models.Profile.objects.create)(user=user)
        return user

    """

    @strawberry.mutation
    async def add_review_to_project(self, info: Info, project_id: strawberry.ID, data: ReviewDataInput) -> types.Review:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required.")

        def _create_sync():
            with transaction.atomic():
                project = models.Project.objects.get(pk=project_id)

                models.Review.objects.filter(
                    user=user,
                    object_id=project.id,
                    content_type__model='project',
                    is_latest=True
                ).update(is_latest=False)

                old_reviews_count = project.reviews_count
                old_star_total = project.star_average * old_reviews_count

                review = models.Review.objects.create(
                    user=user,
                    stars=data.stars,
                    text=data.text,
                    content_object=project
                )

                new_reviews_count = old_reviews_count + 1
                new_star_total = old_star_total + float(data.stars)
                new_average = new_star_total / new_reviews_count if new_reviews_count > 0 else 0.0

                project.reviews_count = new_reviews_count
                project.star_average = new_average
                project.save(update_fields=['reviews_count', 'star_average'])

            return review

        return await database_sync_to_async(_create_sync)()


    @strawberry.mutation
    async def add_review_to_song(self, info: Info, song_id: strawberry.ID, data: ReviewDataInput) -> types.Review:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required.")

        def _create_sync():
            with transaction.atomic():
                song = models.Song.objects.get(pk=song_id)

                models.Review.objects.filter(
                    user=user,
                    object_id=song.id,
                    content_type__model='song',
                    is_latest=True
                ).update(is_latest=False)

                old_reviews_count = song.reviews_count
                old_star_total = song.star_average * old_reviews_count

                review = models.Review.objects.create(
                    user=user,
                    stars=data.stars,
                    text=data.text,
                    content_object=song
                )

                new_reviews_count = old_reviews_count + 1
                new_star_total = old_star_total + float(data.stars)
                new_average = new_star_total / new_reviews_count if new_reviews_count > 0 else 0.0

                song.reviews_count = new_reviews_count
                song.star_average = new_average
                song.save(update_fields=['reviews_count', 'star_average'])

            return review

        return await database_sync_to_async(_create_sync)()


    @strawberry.mutation
    async def add_review_to_outfit(self, info: Info, outfit_id: strawberry.ID, data: ReviewDataInput) -> types.Review:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required.")

        def _create_sync():
            with transaction.atomic():
                outfit = models.Outfit.objects.get(pk=outfit_id)

                models.Review.objects.filter(
                    user=user,
                    object_id=outfit.id,
                    content_type__model='outfit',
                    is_latest=True
                ).update(is_latest=False)

                old_reviews_count = outfit.reviews_count
                old_star_total = outfit.star_average * old_reviews_count

                review = models.Review.objects.create(
                    user=user,
                    stars=data.stars,
                    text=data.text,
                    content_object=outfit
                )

                new_reviews_count = old_reviews_count + 1
                new_star_total = old_star_total + float(data.stars)
                new_average = new_star_total / new_reviews_count if new_reviews_count > 0 else 0.0

                outfit.reviews_count = new_reviews_count
                outfit.star_average = new_average
                outfit.save(update_fields=['reviews_count', 'star_average'])

            return review

        return await database_sync_to_async(_create_sync)()


    @strawberry.mutation
    async def add_review_to_podcast(self, info: Info, podcast_id: strawberry.ID, data: ReviewDataInput) -> types.Review:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required.")

        def _create_sync():
            with transaction.atomic():
                podcast = models.Outfit.objects.get(pk=podcast_id)

                models.Review.objects.filter(
                    user=user,
                    object_id=podcast.id,
                    content_type__model='podcast',
                    is_latest=True
                ).update(is_latest=False)

                old_reviews_count = podcast.reviews_count
                old_star_total = podcast.star_average * old_reviews_count

                review = models.Review.objects.create(
                    user=user,
                    stars=data.stars,
                    text=data.text,
                    content_object=podcast
                )

                new_reviews_count = old_reviews_count + 1
                new_star_total = old_star_total + float(data.stars)
                new_average = new_star_total / new_reviews_count if new_reviews_count > 0 else 0.0

                podcast.reviews_count = new_reviews_count
                podcast.star_average = new_average
                podcast.save(update_fields=['reviews_count', 'star_average'])

            return review

        return await database_sync_to_async(_create_sync)()


    @strawberry.mutation
    async def add_review_to_music_video(self, info: Info, music_video_id: strawberry.ID,
                                        data: ReviewDataInput) -> types.Review:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required.")

        def _create_sync():
            with transaction.atomic():
                music_video = models.Outfit.objects.get(pk=music_video_id)

                models.Review.objects.filter(
                    user=user,
                    object_id=music_video.id,
                    content_type__model='music_video',
                    is_latest=True
                ).update(is_latest=False)

                old_reviews_count = music_video.reviews_count
                old_star_total = music_video.star_average * old_reviews_count

                review = models.Review.objects.create(
                    user=user,
                    stars=data.stars,
                    text=data.text,
                    content_object=music_video
                )

                new_reviews_count = old_reviews_count + 1
                new_star_total = old_star_total + float(data.stars)
                new_average = new_star_total / new_reviews_count if new_reviews_count > 0 else 0.0

                music_video.reviews_count = new_reviews_count
                music_video.star_average = new_average
                music_video.save(update_fields=['reviews_count', 'star_average'])

            return review

        return await database_sync_to_async(_create_sync)()


    @strawberry.mutation
    async def add_review_to_cover(self, info: Info, cover_id: strawberry.ID, data: ReviewDataInput) -> types.Review:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required.")

        def _create_sync():
            with transaction.atomic():
                cover = models.Outfit.objects.get(pk=cover_id)

                models.Review.objects.filter(
                    user=user,
                    object_id=cover.id,
                    content_type__model='cover',
                    is_latest=True
                ).update(is_latest=False)

                old_reviews_count = cover.reviews_count
                old_star_total = cover.star_average * old_reviews_count

                review = models.Review.objects.create(
                    user=user,
                    stars=data.stars,
                    text=data.text,
                    content_object=cover
                )

                new_reviews_count = old_reviews_count + 1
                new_star_total = old_star_total + float(data.stars)
                new_average = new_star_total / new_reviews_count if new_reviews_count > 0 else 0.0

                cover.reviews_count = new_reviews_count
                cover.star_average = new_average
                cover.save(update_fields=['reviews_count', 'star_average'])

            return review

        return await database_sync_to_async(_create_sync)()


    @strawberry.mutation
    async def add_sub_review_to_review(self, info: Info, review_id: strawberry.ID,
                                       data: SubReviewDataInput) -> types.SubReview:
        def _create_sync():

            review = models.Review.objects.get(pk=review_id)
            sub_review = models.SubReview.objects.create(
                review=review,
                topic=data.topic,
                text=data.text,
                stars=data.stars
            )
            return sub_review

        return await database_sync_to_async(_create_sync)()


    """
    @strawberry.mutation
    async def create_conversation(self, info: Info, data: ConversationCreateInput) -> types.Conversation:
        # Get the request from the context, which is safe to do here.
        request = info.context.request

        # Define a synchronous inner function to handle all database logic.
        def _create_conversation_sync():
            user = request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            # Ensure the current user is always a participant
            participant_ids = set(data.participant_ids)
            participant_ids.add(str(user.id))

            if len(participant_ids) < 2:
                raise Exception("A conversation requires at least two participants.")

            # Check if a conversation with these exact participants already exists
            # This is all synchronous code now, so we don't need await.
            existing_conversation = (
                models.Conversation.objects.annotate(p_count=Count('participants'))
                .filter(p_count=len(participant_ids))
                .filter(participants__in=participant_ids)
                .first()
            )

            if existing_conversation:
                return existing_conversation

            # If no conversation exists, create a new one
            new_conversation = models.Conversation.objects.create()
            participants = list(User.objects.filter(id__in=participant_ids))
            new_conversation.participants.set(participants)
            return new_conversation

        # Now, call the synchronous function from our async context
        return await database_sync_to_async(_create_conversation_sync)()
    """

    """
    @strawberry.mutation
    async def add_message_to_conversation(self, info: Info, conversation_id: strawberry.ID,
                                          data: MessageDataInput) -> types.Message:
        # First, get the request from the info object in the async scope.
        request = info.context.request

        # Define a synchronous inner function to handle all database logic.
        def _add_message_sync():
            user = request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            conversation = models.Conversation.objects.get(pk=conversation_id)

            # Verify user is a participant
            if not conversation.participants.filter(id=user.id).exists():
                raise Exception("You are not a participant in this conversation.")

            # Create the message
            message = models.Message.objects.create(
                conversation=conversation,
                sender=user,
                text=data.text
            )

            # Update the conversation's latest message details
            conversation.latest_message = message
            conversation.latest_message_text = message.text
            conversation.latest_message_time = message.time
            conversation.latest_message_sender = user
            conversation.save(
                update_fields=['latest_message', 'latest_message_text', 'latest_message_time', 'latest_message_sender']
            )

            return message

        # Call the synchronous function safely from our async context
        return await database_sync_to_async(_add_message_sync)()
    """

    """
    @strawberry.mutation
    async def delete_message(self, info: Info, id: strawberry.ID) -> SuccessMessage:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required.")

        message = await database_sync_to_async(models.Message.objects.filter(pk=id).first)()
        if not message:
            raise Exception("Message not found.")

        if message.sender != user:
            raise Exception("You can only delete your own messages.")

        await database_sync_to_async(message.delete)()
        return SuccessMessage(message="Message deleted successfully.")
    """

    """
    @strawberry.mutation
    async def like_message(self, info: Info, id: strawberry.ID) -> types.Message:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required.")

        message = await database_sync_to_async(models.Message.objects.get)(pk=id)

        is_participant = await database_sync_to_async(message.conversation.participants.filter(id=user.id).exists)()
        if not is_participant:
            raise Exception("You must be in the conversation to like a message.")

        is_liked = await database_sync_to_async(message.liked_by.filter(id=user.id).exists)()

        if is_liked:
            await database_sync_to_async(message.liked_by.remove)(user)
        else:
            await database_sync_to_async(message.liked_by.add)(user)

        return message
    """

    """
    @strawberry.mutation
    async def mark_message_as_read(self, info: Info, id: strawberry.ID) -> types.Message:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required.")

        message = await database_sync_to_async(models.Message.objects.get)(pk=id)

        is_participant = await database_sync_to_async(message.conversation.participants.filter(id=user.id).exists)()
        if not is_participant:
            raise Exception("You are not a participant in this conversation.")

        if message.sender == user:
            return message

        message.is_read = True
        await database_sync_to_async(message.save)(update_fields=['is_read'])
        return message
    """

    """
    @strawberry.mutation
    async def add_artist_to_song(self, info: Info, song_id: strawberry.ID, artist_id: strawberry.ID,
                                 position: int) -> types.SongArtist:
        song = await database_sync_to_async(models.Song.objects.get)(pk=song_id)
        artist = await database_sync_to_async(models.Artist.objects.get)(pk=artist_id)
        song_artist = await database_sync_to_async(models.SongArtist.objects.create)(song=song, artist=artist,
                                                                                     position=position)
        return song_artist
    """

    """
    @strawberry.mutation
    async def add_artist_to_project(self, info: Info, project_id: strawberry.ID, artist_id: strawberry.ID,
                                    position: int) -> types.ProjectArtist:
        project = await database_sync_to_async(models.Project.objects.get)(pk=project_id)
        artist = await database_sync_to_async(models.Artist.objects.get)(pk=artist_id)
        project_artist = await database_sync_to_async(models.ProjectArtist.objects.create)(project=project,
                                                                                           artist=artist,
                                                                                           position=position)
        return project_artist
    """

    """
    @strawberry.mutation
    async def add_song_to_project(self, info: Info, project_id: strawberry.ID, song_id: strawberry.ID,
                                  position: int) -> types.ProjectSong:
        project = await database_sync_to_async(models.Project.objects.get)(pk=project_id)
        song = await database_sync_to_async(models.Song.objects.get)(pk=song_id)
        project_song = await database_sync_to_async(models.ProjectSong.objects.create)(project=project, song=song,
                                                                                       position=position)
        return project_song
    """

    """
    @strawberry.mutation
    async def add_cover_to_project(self, info: Info, project_id: strawberry.ID, data: CoverDataInput) -> types.Cover:
        project = await database_sync_to_async(models.Project.objects.get)(pk=project_id)
        cover = await database_sync_to_async(models.Cover.objects.create)(image=data.image_url, content_object=project)
        return cover
    """

    """
    @strawberry.mutation
    async def follow_user(self, info: Info, follower_id: strawberry.ID, followed_id: strawberry.ID) -> types.Profile:
        # Note: This is insecure, should use authenticated user
        user = info.context.request.user
        if not user.is_authenticated or str(user.id) != str(follower_id):
            raise Exception("Permission denied.")

        follower_profile = await database_sync_to_async(models.Profile.objects.get)(user__pk=follower_id)
        followed_profile = await database_sync_to_async(models.Profile.objects.get)(user__pk=followed_id)

        await database_sync_to_async(follower_profile.following.add)(followed_profile)

        follower_profile.following_count = await database_sync_to_async(follower_profile.following.count)()
        followed_profile.followers_count = await database_sync_to_async(followed_profile.followers.count)()

        await database_sync_to_async(follower_profile.save)()
        await database_sync_to_async(followed_profile.save)()
        return followed_profile
    """

    """
    @strawberry.mutation
    async def change_my_password(self, info: Info, old_password: str, new_password: str) -> SuccessMessage:
        user: User = info.context.request.user
        if not user.is_authenticated:
            raise Exception("You must be logged in to change your password.")

        is_password_correct = await sync_to_async(user.check_password)(old_password)
        if not is_password_correct:
            raise Exception("Incorrect old password.")

        await sync_to_async(password_validation.validate_password)(new_password, user)

        await database_sync_to_async(user.set_password)(new_password)
        await database_sync_to_async(user.save)()
        return SuccessMessage(message="Your password has been successfully changed.")
    """

    """
    @strawberry.mutation
    async def delete_my_account(self, info: Info, password: str) -> SuccessMessage:
        user: User = info.context.request.user
        if not user.is_authenticated:
            raise Exception("You must be logged in to delete your account.")

        is_password_correct = await sync_to_async(user.check_password)(password)
        if not is_password_correct:
            raise Exception("Incorrect password.")

        await database_sync_to_async(user.delete)()
        return SuccessMessage(message="Your account has been successfully deleted.")
    """

    """
    @strawberry.mutation
    async def login_with_google(self, info: Info, access_token: str) -> types.User:
        request = info.context.request
        app = await database_sync_to_async(SocialApp.objects.get)(provider='google')
        token = SocialToken(app=app, token=access_token)
        adapter = GoogleOAuth2Adapter(request)
        login_data = await database_sync_to_async(adapter.complete_login)(request, app, token)
        login_data.state = SocialLogin.state_from_request(request)
        user = await database_sync_to_async(complete_social_login)(request, login_data)
        if not user.is_authenticated:
            raise Exception("Google authentication failed.")
        return user
    """

    """
    @strawberry.mutation
    async def login_with_apple(self, info: Info, access_token: str, id_token: str) -> types.User:
        request = info.context.request
        app = await database_sync_to_async(SocialApp.objects.get)(provider='apple')
        token = SocialToken(app=app, token=access_token)
        request.POST = request.POST.copy()
        request.POST['id_token'] = id_token
        adapter = AppleOAuth2Adapter(request)
        login_data = await database_sync_to_async(adapter.complete_login)(request, app, token)
        login_data.state = SocialLogin.state_from_request(request)
        user = await database_sync_to_async(complete_social_login)(request, login_data)
        if not user.is_authenticated:
            raise Exception("Apple authentication failed.")
        return user
    """