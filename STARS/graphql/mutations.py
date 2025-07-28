# STARS/graphql/mutations.py

import strawberry
import strawberry_django
from strawberry import auto
from typing import List, Optional
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from django.utils import timezone
from strawberry.types import Info
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.contrib.auth import login

# --- IMPORTS FOR MANUAL SOCIAL LOGIN ---
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialApp, SocialLogin, SocialToken
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
import requests  # Make sure 'requests' is in your requirements.txt

from STARS import models
from . import types


# -----------------------------------------------------------------------------
# Input Types (Stable Pattern)
# -----------------------------------------------------------------------------
# ... (all your existing input types remain the same) ...
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


@strawberry_django.input(models.EventSeries)
class EventSeriesCreateInput:
    name: auto
    description: Optional[str] = None
    is_featured: Optional[bool] = False


@strawberry.input
class EventSeriesUpdateInput:
    id: strawberry.ID
    name: Optional[str] = strawberry.UNSET
    description: Optional[str] = strawberry.UNSET
    is_featured: Optional[bool] = strawberry.UNSET


@strawberry_django.input(models.Event)
class EventCreateInput:
    name: auto
    date: auto
    location: Optional[str] = None
    is_one_time: Optional[bool] = False
    series_id: Optional[strawberry.ID] = None
    is_featured: Optional[bool] = False


@strawberry.input
class EventUpdateInput:
    id: strawberry.ID
    name: Optional[str] = strawberry.UNSET
    date: Optional[str] = strawberry.UNSET
    location: Optional[str] = strawberry.UNSET
    is_one_time: Optional[bool] = strawberry.UNSET
    series_id: Optional[strawberry.ID] = strawberry.UNSET
    is_featured: Optional[bool] = strawberry.UNSET


@strawberry_django.input(models.Review)
class ReviewCreateInput:
    user_id: strawberry.ID
    stars: auto
    text: Optional[str] = None
    is_latest: Optional[bool] = True


@strawberry.input
class ReviewUpdateInput:
    id: strawberry.ID
    stars: Optional[float] = strawberry.UNSET
    text: Optional[str] = strawberry.UNSET
    is_latest: Optional[bool] = strawberry.UNSET


@strawberry.input
class ReviewDataInput:
    stars: float
    text: str


@strawberry_django.input(models.SubReview)
class SubReviewCreateInput:
    review_id: strawberry.ID
    topic: auto
    stars: auto
    text: Optional[str] = None


@strawberry.input
class SubReviewUpdateInput:
    id: strawberry.ID
    topic: Optional[str] = strawberry.UNSET
    text: Optional[str] = strawberry.UNSET
    stars: Optional[float] = strawberry.UNSET


@strawberry.input
class SubReviewDataInput:
    topic: str
    text: str
    stars: float


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


@strawberry.type
class SuccessMessage:
    message: str


@strawberry.type
class Mutation:
    # ... (all your existing mutations remain the same) ...
    create_artist: types.Artist = strawberry_django.mutations.create(ArtistCreateInput)
    update_artist: types.Artist = strawberry_django.mutations.update(ArtistUpdateInput)
    delete_artist: types.Artist = strawberry_django.mutations.delete(strawberry.ID)

    create_project: types.Project = strawberry_django.mutations.create(ProjectCreateInput)
    update_project: types.Project = strawberry_django.mutations.update(ProjectUpdateInput)
    delete_project: types.Project = strawberry_django.mutations.delete(strawberry.ID)

    create_song: types.Song = strawberry_django.mutations.create(SongCreateInput)
    update_song: types.Song = strawberry_django.mutations.update(SongUpdateInput)
    delete_song: types.Song = strawberry_django.mutations.delete(strawberry.ID)

    create_event_series: types.EventSeries = strawberry_django.mutations.create(EventSeriesCreateInput)
    update_event_series: types.EventSeries = strawberry_django.mutations.update(EventSeriesUpdateInput)
    delete_event_series: types.EventSeries = strawberry_django.mutations.delete(strawberry.ID)
    create_event: types.Event = strawberry_django.mutations.create(EventCreateInput)
    update_event: types.Event = strawberry_django.mutations.update(EventUpdateInput)
    delete_event: types.Event = strawberry_django.mutations.delete(strawberry.ID)

    create_review: types.Review = strawberry_django.mutations.create(ReviewCreateInput)
    update_review: types.Review = strawberry_django.mutations.update(ReviewUpdateInput)
    delete_review: types.Review = strawberry_django.mutations.delete(strawberry.ID)

    create_music_video: types.MusicVideo = strawberry_django.mutations.create(MusicVideoCreateInput)
    update_music_video: types.MusicVideo = strawberry_django.mutations.update(MusicVideoUpdateInput)
    delete_music_video: types.MusicVideo = strawberry_django.mutations.delete(strawberry.ID)
    create_podcast: types.Podcast = strawberry_django.mutations.create(PodcastCreateInput)
    update_podcast: types.Podcast = strawberry_django.mutations.update(PodcastUpdateInput)
    delete_podcast: types.Podcast = strawberry_django.mutations.delete(strawberry.ID)
    create_outfit: types.Outfit = strawberry_django.mutations.create(OutfitCreateInput)
    update_outfit: types.Outfit = strawberry_django.mutations.update(OutfitUpdateInput)
    delete_outfit: types.Outfit = strawberry_django.mutations.delete(strawberry.ID)

    update_profile: types.Profile = strawberry_django.mutations.update(ProfileUpdateInput)

    @strawberry.mutation
    async def signup(self, data: SignupInput) -> types.User:
        if data.password != data.password_confirmation:
            raise Exception("Passwords do not match.")

        user_exists = await sync_to_async(User.objects.filter(email=data.email).exists)()
        if user_exists:
            raise Exception("A user with this email already exists.")

        username_exists = await sync_to_async(User.objects.filter(username=data.username).exists)()
        if username_exists:
            raise Exception("A user with this username already exists.")

        try:
            await sync_to_async(password_validation.validate_password)(data.password)
        except ValidationError as e:
            raise Exception(f"Invalid password: {', '.join(e.messages)}")

        user = await sync_to_async(User.objects.create_user)(
            username=data.username,
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
        )
        await sync_to_async(models.Profile.objects.create)(user=user)
        return user

    @strawberry.mutation
    async def add_review_to_project(self, info, project_id: strawberry.ID, user_id: strawberry.ID,
                                    data: ReviewDataInput) -> types.Review:
        project = await sync_to_async(models.Project.objects.get)(pk=project_id)
        user = await sync_to_async(User.objects.get)(pk=user_id)
        review = await sync_to_async(models.Review.objects.create)(user=user, stars=data.stars, text=data.text,
                                                                   content_object=project)
        return review

    @strawberry.mutation
    async def add_review_to_song(self, info, song_id: strawberry.ID, user_id: strawberry.ID,
                                 data: ReviewDataInput) -> types.Review:
        song = await sync_to_async(models.Song.objects.get)(pk=song_id)
        user = await sync_to_async(User.objects.get)(pk=user_id)
        review = await sync_to_async(models.Review.objects.create)(user=user, stars=data.stars, text=data.text,
                                                                   content_object=song)
        return review

    @strawberry.mutation
    async def add_review_to_outfit(self, info, outfit_id: strawberry.ID, user_id: strawberry.ID,
                                   data: ReviewDataInput) -> types.Review:
        outfit = await sync_to_async(models.Outfit.objects.get)(pk=outfit_id)
        user = await sync_to_async(User.objects.get)(pk=user_id)
        review = await sync_to_async(models.Review.objects.create)(user=user, stars=data.stars, text=data.text,
                                                                   content_object=outfit)
        return review

    @strawberry.mutation
    async def add_review_to_podcast(self, info, podcast_id: strawberry.ID, user_id: strawberry.ID,
                                    data: ReviewDataInput) -> types.Review:
        podcast = await sync_to_async(models.Podcast.objects.get)(pk=podcast_id)
        user = await sync_to_async(User.objects.get)(pk=user_id)
        review = await sync_to_async(models.Review.objects.create)(user=user, stars=data.stars, text=data.text,
                                                                   content_object=podcast)
        return review

    @strawberry.mutation
    async def add_review_to_music_video(self, info, music_video_id: strawberry.ID, user_id: strawberry.ID,
                                        data: ReviewDataInput) -> types.Review:
        music_video = await sync_to_async(models.MusicVideo.objects.get)(pk=music_video_id)
        user = await sync_to_async(User.objects.get)(pk=user_id)
        review = await sync_to_async(models.Review.objects.create)(user=user, stars=data.stars, text=data.text,
                                                                   content_object=music_video)
        return review

    @strawberry.mutation
    async def add_review_to_cover(self, info, cover_id: strawberry.ID, user_id: strawberry.ID,
                                  data: ReviewDataInput) -> types.Review:
        cover = await sync_to_async(models.Cover.objects.get)(pk=cover_id)
        user = await sync_to_async(User.objects.get)(pk=user_id)
        review = await sync_to_async(models.Review.objects.create)(user=user, stars=data.stars, text=data.text,
                                                                   content_object=cover)
        return review

    @strawberry.mutation
    async def add_sub_review_to_review(self, info, review_id: strawberry.ID,
                                       data: SubReviewDataInput) -> types.SubReview:
        review = await sync_to_async(models.Review.objects.get)(pk=review_id)
        sub_review = await sync_to_async(models.SubReview.objects.create)(
            review=review,
            topic=data.topic,
            text=data.text,
            stars=data.stars
        )
        return sub_review

    @strawberry.mutation
    async def add_message_to_conversation(self, info, conversation_id: strawberry.ID, sender_id: strawberry.ID,
                                          data: MessageDataInput) -> types.Message:
        conversation = await sync_to_async(models.Conversation.objects.get)(pk=conversation_id)
        sender = await sync_to_async(User.objects.get)(pk=sender_id)

        message = await sync_to_async(models.Message.objects.create)(
            conversation=conversation,
            sender=sender,
            text=data.text
        )

        conversation.latest_message = message
        conversation.latest_message_text = message.text
        conversation.latest_message_time = message.time
        conversation.latest_message_sender = sender
        await sync_to_async(conversation.save)()

        return message

    @strawberry.mutation
    async def add_artist_to_song(self, info, song_id: strawberry.ID, artist_id: strawberry.ID,
                                 position: int) -> types.SongArtist:
        song = await sync_to_async(models.Song.objects.get)(pk=song_id)
        artist = await sync_to_async(models.Artist.objects.get)(pk=artist_id)
        song_artist = await sync_to_async(models.SongArtist.objects.create)(song=song, artist=artist, position=position)
        return song_artist

    @strawberry.mutation
    async def add_artist_to_project(self, info, project_id: strawberry.ID, artist_id: strawberry.ID,
                                    position: int) -> types.ProjectArtist:
        project = await sync_to_async(models.Project.objects.get)(pk=project_id)
        artist = await sync_to_async(models.Artist.objects.get)(pk=artist_id)
        project_artist = await sync_to_async(models.ProjectArtist.objects.create)(project=project, artist=artist,
                                                                                  position=position)
        return project_artist

    @strawberry.mutation
    async def add_song_to_project(self, info, project_id: strawberry.ID, song_id: strawberry.ID,
                                  position: int) -> types.ProjectSong:
        project = await sync_to_async(models.Project.objects.get)(pk=project_id)
        song = await sync_to_async(models.Song.objects.get)(pk=song_id)
        project_song = await sync_to_async(models.ProjectSong.objects.create)(project=project, song=song,
                                                                              position=position)
        return project_song

    @strawberry.mutation
    async def add_cover_to_project(self, info, project_id: strawberry.ID, data: CoverDataInput) -> types.Cover:
        project = await sync_to_async(models.Project.objects.get)(pk=project_id)
        cover = await sync_to_async(models.Cover.objects.create)(image=data.image_url, content_object=project)
        return cover

    @strawberry.mutation
    async def follow_user(self, info, follower_id: strawberry.ID, followed_id: strawberry.ID) -> types.Profile:
        follower_profile = await sync_to_async(models.Profile.objects.get)(user__pk=follower_id)
        followed_profile = await sync_to_async(models.Profile.objects.get)(user__pk=followed_id)

        await sync_to_async(follower_profile.following.add)(followed_profile)

        follower_profile.following_count = await sync_to_async(follower_profile.following.count)()
        followed_profile.followers_count = await sync_to_async(followed_profile.followers.count)()

        await sync_to_async(follower_profile.save)()
        await sync_to_async(followed_profile.save)()

        return followed_profile

    @strawberry.mutation
    async def change_my_password(self, info: Info, old_password: str, new_password: str) -> SuccessMessage:
        user: User = info.context.request.user

        if not user.is_authenticated:
            raise Exception("You must be logged in to change your password.")

        is_password_correct = await sync_to_async(user.check_password)(old_password)
        if not is_password_correct:
            raise Exception("Incorrect old password.")

        await sync_to_async(password_validation.validate_password)(new_password, user)

        await sync_to_async(user.set_password)(new_password)
        await sync_to_async(user.save)()

        return SuccessMessage(message="Your password has been successfully changed.")

    @strawberry.mutation
    async def delete_my_account(self, info: Info, password: str) -> SuccessMessage:
        user: User = info.context.request.user

        if not user.is_authenticated:
            raise Exception("You must be logged in to delete your account.")

        is_password_correct = await sync_to_async(user.check_password)(password)
        if not is_password_correct:
            raise Exception("Incorrect password.")

        await sync_to_async(user.delete)()

        return SuccessMessage(message="Your account has been successfully deleted.")

    # --- NEW MANUAL SOCIAL LOGIN MUTATIONS ---
    @strawberry.mutation
    async def login_with_google(self, info: Info, access_token: str) -> types.User:
        request = info.context.request

        # 1. Get the SocialApp for Google
        app = await sync_to_async(SocialApp.objects.get)(provider='google')

        # 2. Create a SocialToken
        token = SocialToken(app=app, token=access_token)

        # 3. Use the adapter to complete the login
        adapter = GoogleOAuth2Adapter(request)
        login_data = await sync_to_async(adapter.complete_login)(request, app, token)

        # 4. Perform the actual login
        login_data.state = SocialLogin.state_from_request(request)
        user = await sync_to_async(complete_social_login)(request, login_data)

        if not user.is_authenticated:
            raise Exception("Google authentication failed.")

        return user

    @strawberry.mutation
    async def login_with_apple(self, info: Info, access_token: str, id_token: str) -> types.User:
        request = info.context.request

        app = await sync_to_async(SocialApp.objects.get)(provider='apple')
        token = SocialToken(app=app, token=access_token)

        # Apple requires an id_token as well
        request.POST = request.POST.copy()
        request.POST['id_token'] = id_token

        adapter = AppleOAuth2Adapter(request)
        login_data = await sync_to_async(adapter.complete_login)(request, app, token)

        login_data.state = SocialLogin.state_from_request(request)
        user = await sync_to_async(complete_social_login)(request, login_data)

        if not user.is_authenticated:
            raise Exception("Apple authentication failed.")

        return user
