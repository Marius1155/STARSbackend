import strawberry
import strawberry_django
import re
import os
import requests
from strawberry import auto
from typing import List, Optional
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from django.db.models import Count, Q
from strawberry.types import Info
from django.contrib.auth import password_validation, login, authenticate, logout
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
import cloudinary.uploader
import base64
import tempfile
import enum
from datetime import datetime
from .subscriptions import broadcast_conversation_update, broadcast_message_event
import asyncio



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


YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

from urllib.parse import urlparse, parse_qs

def clean_youtube_url(url: str) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if 'v' in query:
        return f"https://www.youtube.com/watch?v={query['v'][0]}"
    elif parsed.netloc.endswith("youtu.be"):
        return url  # already short URL
    else:
        raise ValueError("Cannot extract video ID from URL")

def extract_youtube_id(url: str) -> str:
    """
    Extract the 11-character YouTube video ID from any standard YouTube URL.
    Works with URLs like:
    - https://www.youtube.com/watch?v=XXXXXXXXXXX
    - https://youtu.be/XXXXXXXXXXX
    - https://www.youtube.com/watch?v=XXXXXXXXXXX&list=...
    """
    # Try standard v= query parameter
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if 'v' in query:
        video_id = query['v'][0]
        if len(video_id) == 11:
            return video_id

    # Try youtu.be short URL
    match = re.search(r'youtu\.be/([0-9A-Za-z_-]{11})', url)
    if match:
        return match.group(1)

    # Try /embed/ style URLs
    match = re.search(r'/embed/([0-9A-Za-z_-]{11})', url)
    if match:
        return match.group(1)

    raise ValueError(f"Invalid YouTube URL: {url}")


def fetch_youtube_metadata(video_url: str):
    video_id = extract_youtube_id(video_url)
    api_url = (
        f"https://www.googleapis.com/youtube/v3/videos"
        f"?part=snippet&id={video_id}&key={YOUTUBE_API_KEY}"
    )
    response = requests.get(api_url)
    data = response.json()

    if "items" not in data or not data["items"]:
        raise ValueError("Video not found or API limit reached.")

    snippet = data["items"][0]["snippet"]
    title = snippet["title"]
    published_at_str = snippet["publishedAt"][:10]  # "YYYY-MM-DD"
    published_at = datetime.strptime(published_at_str, "%Y-%m-%d").date()
    thumbnail = snippet["thumbnails"]["high"]["url"]

    return title, published_at, thumbnail


@strawberry.input
class MusicVideoInput:
    youtube_url: str
    song_ids: list[strawberry.ID]


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
    instagram_post: auto
    description: Optional[str] = None
    is_featured: Optional[bool] = False
    cover_ids: Optional[list[strawberry.ID]] = strawberry.UNSET
    music_video_ids: Optional[list[strawberry.ID]] = strawberry.UNSET
    event_ids: Optional[list[strawberry.ID]] = strawberry.UNSET
    match_ids: Optional[list[strawberry.ID]] = strawberry.UNSET


@strawberry_django.input(models.Outfit)
class OutfitUpdateInput:
    artist_id: strawberry.ID
    date: str  # ISO format, e.g., "2025-08-16"
    instagram_post: str
    description: Optional[str] = None
    is_featured: Optional[bool] = False
    cover_ids: Optional[list[strawberry.ID]] = strawberry.UNSET
    music_video_ids: Optional[list[strawberry.ID]] = strawberry.UNSET
    event_ids: Optional[list[strawberry.ID]] = strawberry.UNSET
    match_ids: Optional[list[strawberry.ID]] = strawberry.UNSET


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
    replying_to_messsage_id: Optional[strawberry.ID] = None


@strawberry.input
class CoverDataInput:
    image_file: str


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
    update_subreview: types.SubReview = strawberry_django.mutations.update(SubReviewUpdateInput)
    delete_subreview: types.SubReview = strawberry_django.mutations.delete(strawberry.ID)

    update_music_video: types.MusicVideo = strawberry_django.mutations.update(MusicVideoUpdateInput)
    delete_music_video: types.MusicVideo = strawberry_django.mutations.delete(strawberry.ID)
    update_podcast: types.Podcast = strawberry_django.mutations.update(PodcastUpdateInput)
    delete_podcast: types.Podcast = strawberry_django.mutations.delete(strawberry.ID)

    update_outfit: types.Outfit = strawberry_django.mutations.update(OutfitUpdateInput)
    delete_outfit: types.Outfit = strawberry_django.mutations.delete(strawberry.ID)

    update_profile: types.Profile = strawberry_django.mutations.update(ProfileUpdateInput)

    update_comment: types.Comment = strawberry_django.mutations.update(CommentUpdateInput)
    delete_comment: types.Comment = strawberry_django.mutations.delete(strawberry.ID)


    @strawberry.mutation
    async def create_event(self, info: Info, data: EventCreateInput) -> types.Event:

        def _create_sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
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

        def _create_sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                review = models.Review.objects.get(pk=data.review_id)

                comment = models.Comment.objects.create(
                    review=review,
                    user=user,
                    text=data.text
                )
                return comment

        return await database_sync_to_async(_create_sync)()


    @strawberry.mutation
    async def like_dislike_comment(self, info: Info, comment_id: strawberry.ID, action: LikeAction) -> types.Comment:

        def _update_sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                comment = (
                    models.Comment.objects
                    .select_for_update()
                    .get(pk=comment_id)
                )

                if action == LikeAction.LIKE:
                    if not comment.liked_by.filter(pk=user.pk).exists():
                        comment.liked_by.add(user)
                        comment.likes_count += 1
                    if comment.disliked_by.filter(pk=user.pk).exists():
                        comment.disliked_by.remove(user)
                        comment.dislikes_count -= 1

                elif action == LikeAction.UNLIKE:
                    if comment.liked_by.filter(pk=user.pk).exists():
                        comment.liked_by.remove(user)
                        comment.likes_count -= 1

                elif action == LikeAction.DISLIKE:
                    if not comment.disliked_by.filter(pk=user.pk).exists():
                        comment.disliked_by.add(user)
                        comment.dislikes_count += 1
                    if comment.liked_by.filter(pk=user.pk).exists():
                        comment.liked_by.remove(user)
                        comment.likes_count -= 1

                elif action == LikeAction.UNDISLIKE:
                    if comment.disliked_by.filter(pk=user.pk).exists():
                        comment.disliked_by.remove(user)
                        comment.dislikes_count -= 1

                comment.save(update_fields=["likes_count", "dislikes_count"])
                return comment

        return await database_sync_to_async(_update_sync)()


    @strawberry.mutation
    async def like_dislike_review(self, info: Info, review_id: strawberry.ID, action: LikeAction) -> types.Review:

        def _update_sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                review = (
                    models.Review.objects
                    .select_for_update()
                    .get(pk=review_id)
                )

                if action == LikeAction.LIKE:
                    if not review.liked_by.filter(pk=user.pk).exists():
                        review.liked_by.add(user)
                        review.likes_count += 1
                    if review.disliked_by.filter(pk=user.pk).exists():
                        review.disliked_by.remove(user)
                        review.dislikes_count -= 1

                elif action == LikeAction.UNLIKE:
                    if review.liked_by.filter(pk=user.pk).exists():
                        review.liked_by.remove(user)
                        review.likes_count -= 1

                elif action == LikeAction.DISLIKE:
                    if not review.disliked_by.filter(pk=user.pk).exists():
                        review.disliked_by.add(user)
                        review.dislikes_count += 1
                    if review.liked_by.filter(pk=user.pk).exists():
                        review.liked_by.remove(user)
                        review.likes_count -= 1

                elif action == LikeAction.UNDISLIKE:
                    if review.disliked_by.filter(pk=user.pk).exists():
                        review.disliked_by.remove(user)
                        review.dislikes_count -= 1

                review.save(update_fields=["likes_count", "dislikes_count"])
                return review

        return await database_sync_to_async(_update_sync)()


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

    @strawberry.mutation
    async def login_user(self, info: Info, data: LoginInput) -> types.User:
        request = info.context.request

        def _login_sync():
            username_or_email = data.username
            password = data.password

            # Login via email
            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email__iexact=username_or_email)
                except User.DoesNotExist:
                    raise Exception("No account found with this email.")

                user = authenticate(request, username=user_obj.username, password=password)
                if user is None:
                    raise Exception("Incorrect password.")

            # Login via username
            else:
                try:
                    user_obj = User.objects.get(username__iexact=username_or_email)
                except User.DoesNotExist:
                    raise Exception("No account found with this username.")

                user = authenticate(request, username=user_obj.username, password=password)
                if user is None:
                    raise Exception("Incorrect password.")

            login(request, user)
            return user

        return await database_sync_to_async(_login_sync)()

    @strawberry.mutation
    async def logout_user(self, info: Info) -> SuccessMessage:
        request = info.context.request

        def _logout_sync():
            if not request.user.is_authenticated:
                return "User was already logged out."
            logout(request)
            return "Successfully logged out."

        message = await database_sync_to_async(_logout_sync)()
        return SuccessMessage(message=message)


    @strawberry.mutation
    async def signup(self, data: SignupInput) -> types.User:

        def _signup_sync():
            if data.password != data.password_confirmation:
                raise Exception("Passwords do not match.")

            user_exists = User.objects.filter(email__iexact=data.email).exists()
            if user_exists:
                raise Exception("A user with this email already exists.")

            username_exists = User.objects.filter(email__iexact=data.email).exists()
            if username_exists:
                raise Exception("A user with this username already exists.")

            try:
                password_validation.validate_password(data.password)
            except ValidationError as e:
                raise Exception(f"Invalid password: {', '.join(e.messages)}")

            with transaction.atomic():
                user = User.objects.create_user(
                    username=data.username,
                    email=data.email,
                    password=data.password,
                    first_name=data.first_name or "",
                    last_name=data.last_name or ""
                )
                models.Profile.objects.create(user=user)

            return user

        return await database_sync_to_async(_signup_sync)()


    @strawberry.mutation
    async def add_review_to_project(self, info: Info, project_id: strawberry.ID, data: ReviewDataInput) -> types.Review:

        def _create_sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                project = models.Project.objects.select_for_update().get(pk=project_id)

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

        def _create_sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                song = models.Song.objects.select_for_update().get(pk=song_id)

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

        def _create_sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                outfit = models.Outfit.objects.select_for_update().get(pk=outfit_id)

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

        def _create_sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                podcast = models.Outfit.objects.select_for_update().get(pk=podcast_id)

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

        def _create_sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                music_video = models.Outfit.objects.select_for_update().get(pk=music_video_id)

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

        def _create_sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                cover = models.Outfit.objects.select_for_update().get(pk=cover_id)

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
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                review = models.Review.objects.get(pk=review_id)
                sub_review = models.SubReview.objects.create(
                    review=review,
                    topic=data.topic,
                    text=data.text,
                    stars=data.stars
                )
                return sub_review

        return await database_sync_to_async(_create_sync)()


    @strawberry.mutation
    async def delete_review(self, info: Info, review_id: strawberry.ID) -> types.Review:
        def _delete_sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                review = models.Review.objects.filter(pk=review_id).first()
                if not review:
                    raise Exception("Review not found.")

                if review.user != user:
                    raise Exception("You can only delete your own reviews.")

                # Store object info for later
                review_object = review.content_object

                # Delete the review
                review.delete()

                # Find the newest review by this user on the same object
                latest_review = (
                    models.Review.objects.select_for_update().filter(
                        user=user,
                        content_type=review.content_type,
                        object_id=review_object.id,
                    )
                    .order_by('-created_at')
                    .first()
                )
                if latest_review:
                    latest_review.is_latest = True
                    latest_review.save(update_fields=['is_latest'])

                return review

        return await database_sync_to_async(_delete_sync)()


    @strawberry.mutation
    async def create_conversation(self, info: Info, data: ConversationCreateInput) -> types.Conversation:

        def _create_conversation_sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                # Ensure the current user is always a participant
                participant_ids = set(data.participant_ids)
                participant_ids.add(str(user.id))

                if len(participant_ids) < 2:
                    raise Exception("A conversation requires at least two participants.")

                # Check if a conversation with these exact participants already exists
                existing_conversation = (
                    models.Conversation.objects
                    .annotate(
                        total=Count('participants', distinct=True),
                        matched=Count(
                            'participants',
                            filter=Q(participants__id__in=participant_ids),
                            distinct=True
                        ),
                    )
                    .filter(total=len(participant_ids), matched=len(participant_ids))
                    .first()
                )

                if existing_conversation:
                    return existing_conversation

                # If no conversation exists, create a new one
                new_conversation = models.Conversation.objects.create()
                participants = list(User.objects.filter(id__in=participant_ids))
                new_conversation.participants.set(participants)
                return new_conversation

        return await database_sync_to_async(_create_conversation_sync)()

    @strawberry.mutation
    async def add_message_to_conversation(
            self, info: Info, conversation_id: strawberry.ID, data: MessageDataInput
    ) -> types.Message:
        request = info.context.request

        def _add_message_sync():
            user = request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                conversation = models.Conversation.objects.select_for_update().get(pk=conversation_id)

                if not conversation.participants.filter(id=user.id).exists():
                    raise Exception("You are not a participant in this conversation.")

                message_to_reply_to = None
                if data.replying_to_messsage_id:
                    try:
                        message_to_reply_to = models.Message.objects.get(
                            pk=data.replying_to_messsage_id,
                            conversation=conversation
                        )
                    except models.Message.DoesNotExist:
                        raise Exception("The message you are trying to reply to does not exist.")

                message = models.Message.objects.create(
                    conversation=conversation,
                    sender=user,
                    text=data.text,
                    replying_to=message_to_reply_to
                )

                conversation.latest_message = message
                conversation.latest_message_text = message.text
                conversation.latest_message_time = message.time
                conversation.latest_message_sender = user
                conversation.save(update_fields=[
                    'latest_message',
                    'latest_message_text',
                    'latest_message_time',
                    'latest_message_sender'
                ])

                transaction.on_commit(lambda: asyncio.create_task(
                    broadcast_message_event(message, "created")
                ))

                transaction.on_commit(lambda: asyncio.create_task(
                    broadcast_conversation_update(conversation)
                ))

                return message

        return await database_sync_to_async(_add_message_sync)()

    @strawberry.mutation
    async def delete_message(self, info: Info, id: strawberry.ID) -> SuccessMessage:
        def _delete_message_sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                try:
                    message = models.Message.objects.get(pk=id)
                except models.Message.DoesNotExist:
                    raise Exception("Message not found.")

                if message.sender != user:
                    raise Exception("You can only delete your own messages.")

                message.delete()
                return SuccessMessage(message="Message deleted successfully.")

        return await database_sync_to_async(_delete_message_sync)()

    @strawberry.mutation
    async def like_message(self, info: Info, id: strawberry.ID) -> types.Message:
        def _like_message_sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                message = models.Message.objects.select_for_update().get(pk=id)

                is_participant = message.conversation.participants.filter(id=user.id).exists()
                if not is_participant:
                    raise Exception("You must be in the conversation to like a message.")

                is_liked = message.liked_by.filter(id=user.id).exists()

                if is_liked:
                    message.liked_by.remove(user)
                else:
                    message.liked_by.add(user)

                return message

        return await database_sync_to_async(_like_message_sync)()

    @strawberry.mutation
    async def mark_messages_as_read(self, info, conversation_id: strawberry.ID) -> SuccessMessage:
        """Mark all messages from other users in the conversation as read"""
        def _sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                messages = models.Message.objects.filter(
                    conversation_id=conversation_id
                ).exclude(sender=user).filter(is_read=False)
                messages.update(is_read=True)
            return SuccessMessage(message=f"Marked {messages.count()} messages as read.")

        return await database_sync_to_async(_sync)()

    @strawberry.mutation
    async def mark_message_as_delivered(self, info, message_id: strawberry.ID) -> SuccessMessage:
        """Mark a single message as delivered"""

        def _sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                message = models.Message.objects.select_for_update().filter(pk=message_id).first()
                if not message:
                    raise Exception("Message not found.")
                if message.sender == user:
                    raise Exception("Cannot mark your own message as delivered.")
                message.is_delivered = True
                message.save(update_fields=["is_delivered"])
            return SuccessMessage(message="Message marked as delivered.")

        return await database_sync_to_async(_sync)()


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

    @strawberry.mutation
    async def add_cover_to_project(self, info, project_id: strawberry.ID, data: CoverDataInput) -> types.Cover:

        def _sync():

            with transaction.atomic():
                project = models.Project.objects.get(pk=project_id)

                # Determine position
                existing_count = models.Cover.objects.filter(
                    content_type=ContentType.objects.get_for_model(project),
                    object_id=project.id
                ).count()
                position = existing_count + 1

                # Decode and upload base64 image
                image_data = base64.b64decode(data.image_file)
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                temp_file.write(image_data)
                temp_file.flush()

                # Upload to Cloudinary and request colors
                upload_result = cloudinary.uploader.upload(
                    temp_file.name,
                    colors=True,  # This tells Cloudinary to extract the dominant colors
                )
                uploaded_url = upload_result["secure_url"]
                colors = upload_result.get("colors", [])
                primary_color = colors[0][0] if len(colors) > 0 else None
                secondary_color = colors[1][0] if len(colors) > 1 else None

                # Create Cover
                cover = models.Cover.objects.create(
                    image=uploaded_url,
                    content_object=project,
                    position=position,
                    primary_color=primary_color,
                    secondary_color=secondary_color
                )
                return cover

        return await database_sync_to_async(_sync)()


    @strawberry.mutation
    async def add_cover_to_podcast(self, info, podcast_id: strawberry.ID, data: CoverDataInput) -> types.Cover:

        def _sync():

            with transaction.atomic():
                podcast = models.Podcast.objects.get(pk=podcast_id)

                existing_count = models.Cover.objects.filter(
                    content_type=ContentType.objects.get_for_model(podcast),
                    object_id=podcast.id
                ).count()
                position = existing_count + 1

                image_data = base64.b64decode(data.image_file)
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                temp_file.write(image_data)
                temp_file.flush()

                upload_result = cloudinary.uploader.upload(
                    temp_file.name,
                    colors=True
                )
                uploaded_url = upload_result["secure_url"]
                colors = upload_result.get("colors", [])
                primary_color = colors[0][0] if len(colors) > 0 else None
                secondary_color = colors[1][0] if len(colors) > 1 else None

                cover = models.Cover.objects.create(
                    image=uploaded_url,
                    content_object=podcast,
                    position=position,
                    primary_color=primary_color,
                    secondary_color=secondary_color
                )
                return cover

        return await database_sync_to_async(_sync)()


    @strawberry.mutation
    async def add_music_video(self, info, data: MusicVideoInput) -> types.MusicVideo:

        def _sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            clean_url = clean_youtube_url(data.youtube_url)
            title, published_at, thumbnail_url = fetch_youtube_metadata(clean_url)

            import urllib.request
            import tempfile
            image_data = urllib.request.urlopen(thumbnail_url).read()
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            temp_file.write(image_data)
            temp_file.flush()

            upload_result = cloudinary.uploader.upload(
                temp_file.name,
                colors=True,
                transformation=[
                    {"width": 1280, "height": 720, "crop": "fill", "gravity": "center"}
                ]
            )
            uploaded_url = upload_result["secure_url"]
            colors = upload_result.get("colors", [])
            primary_color = colors[0][0] if len(colors) > 0 else None
            secondary_color = colors[1][0] if len(colors) > 1 else None

            with transaction.atomic():
                mv = models.MusicVideo.objects.create(
                    title=title,
                    release_date=published_at,
                    youtube=data.youtube_url,
                    thumbnail=uploaded_url,
                    primary_color=primary_color,
                    secondary_color=secondary_color,
                    number_of_songs=len(data.song_ids)
                )

                songs = list(models.Song.objects.filter(pk__in=data.song_ids))
                mv.songs.set(songs)

            return mv

        return await database_sync_to_async(_sync)()


    @strawberry.mutation
    async def follow_or_unfollow_user(self, info: Info, follower_id: strawberry.ID, followed_id: strawberry.ID) -> types.Profile:
        def _sync():
            user = info.context.request.user
            if not user.is_authenticated or str(user.id) != str(follower_id):
                raise Exception("Permission denied.")

            with transaction.atomic():
                follower_profile = models.Profile.objects.select_for_update().get(user__pk=follower_id)
                followed_profile = models.Profile.objects.select_for_update().get(user__pk=followed_id)

                # Toggle follow/unfollow
                if followed_profile in follower_profile.following.all():
                    follower_profile.following.remove(followed_profile)
                    follower_profile.following_count = max(0, follower_profile.following_count - 1)
                    followed_profile.followers_count = max(0, followed_profile.followers_count - 1)
                else:
                    follower_profile.following.add(followed_profile)
                    follower_profile.following_count += 1
                    followed_profile.followers_count += 1

                follower_profile.save(update_fields=["following_count"])
                followed_profile.save(update_fields=["followers_count"])

                return followed_profile

        return await database_sync_to_async(_sync)()

    @strawberry.mutation
    async def change_my_password(self, info: Info, old_password: str, new_password: str) -> SuccessMessage:

        def _sync_change_password():
            user: User = info.context.request.user
            if not user.is_authenticated:
                raise Exception("You must be logged in to change your password.")

            # Check the old password
            if not user.check_password(old_password):
                raise Exception("Incorrect old password.")

            # Validate the new password
            password_validation.validate_password(new_password, user)

            # Update password and save
            user.set_password(new_password)
            user.save()

            return SuccessMessage(message="Your password has been successfully changed.")

        return await database_sync_to_async(_sync_change_password)()

    @strawberry.mutation
    async def change_my_display_name(self, info: Info, new_display_name: str) -> SuccessMessage:

        def _sync_change_display_name():
            user: User = info.context.request.user
            if not user.is_authenticated:
                raise Exception("You must be logged in to change your first name.")

            user.first_name = new_display_name
            user.save(update_fields=["first_name"])

            return SuccessMessage(message="Your first name has been updated.")

        return await database_sync_to_async(_sync_change_display_name)()

    @strawberry.mutation
    async def change_my_username(self, info: Info, new_username: str) -> SuccessMessage:

        def _sync_change_username():
            user: User = info.context.request.user
            if not user.is_authenticated:
                raise Exception("You must be logged in to change your username.")

            if User.objects.filter(username__iexact=new_username).exclude(pk=user.pk).exists():
                raise Exception("This username is already taken.")

            user.username = new_username
            user.save(update_fields=["username"])

            return SuccessMessage(message="Your username has been updated.")

        return await database_sync_to_async(_sync_change_username)()


    @strawberry.mutation
    async def set_profile_premium(self, info: Info, has_premium: bool) -> SuccessMessage:

        def _sync_set_profile_premium():
            user: User = info.context.request.user
            if not user.is_authenticated:
                raise Exception("You must be logged in to update your profile.")

            with transaction.atomic():
                profile = models.Profile.objects.select_for_update().get(user=user)
                profile.has_premium = has_premium
                profile.save(update_fields=["has_premium"])

                return SuccessMessage(message=f"Premium status set to {has_premium}.")

        return await database_sync_to_async(_sync_set_profile_premium)()


    @strawberry.mutation
    async def delete_my_account(self, info: Info, password: str) -> SuccessMessage:

        def _sync_delete_account():
            user: User = info.context.request.user
            if not user.is_authenticated:
                raise Exception("You must be logged in to delete your account.")

            # Check password
            if not user.check_password(password):
                raise Exception("Incorrect password.")

            # Delete the user
            user.delete()

            return SuccessMessage(message="Your account has been successfully deleted.")

        return await database_sync_to_async(_sync_delete_account)()


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