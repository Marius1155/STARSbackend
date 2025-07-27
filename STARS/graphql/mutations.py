# STARS/graphql/mutations.py

import strawberry
import strawberry_django
from strawberry import auto
from typing import List, Optional
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

from STARS import models
from . import types


# -----------------------------------------------------------------------------
# Input Types (Stable Pattern)
# -----------------------------------------------------------------------------
# Create inputs are generated automatically.
# Update inputs are defined manually, with each field being Optional.

@strawberry_django.input(models.Artist)
class ArtistCreateInput:
    name: auto
    picture: auto
    bio: auto
    wikipedia: auto
    pronouns: auto
    birthdate: auto
    origin: auto


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


@strawberry_django.input(models.EventSeries)
class EventSeriesCreateInput:
    name: auto
    description: auto


@strawberry.input
class EventSeriesUpdateInput:
    id: strawberry.ID
    name: Optional[str] = strawberry.UNSET
    description: Optional[str] = strawberry.UNSET


@strawberry_django.input(models.Event)
class EventCreateInput:
    name: auto
    date: auto
    location: auto
    is_one_time: auto
    series_id: Optional[strawberry.ID] = None


@strawberry.input
class EventUpdateInput:
    id: strawberry.ID
    name: Optional[str] = strawberry.UNSET
    date: Optional[str] = strawberry.UNSET
    location: Optional[str] = strawberry.UNSET
    is_one_time: Optional[bool] = strawberry.UNSET
    series_id: Optional[strawberry.ID] = strawberry.UNSET


@strawberry_django.input(models.Review)
class ReviewCreateInput:
    user_id: strawberry.ID
    stars: auto
    text: auto


@strawberry.input
class ReviewUpdateInput:
    id: strawberry.ID
    stars: Optional[float] = strawberry.UNSET
    text: Optional[str] = strawberry.UNSET


# --- NEW INPUT TYPE FOR REVIEW DATA ---
@strawberry.input
class ReviewDataInput:
    stars: float
    text: str


@strawberry_django.input(models.SubReview)
class SubReviewCreateInput:
    review_id: strawberry.ID
    topic: auto
    text: auto
    stars: auto


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


@strawberry.input
class MusicVideoUpdateInput:
    id: strawberry.ID
    title: Optional[str] = strawberry.UNSET
    release_date: Optional[str] = strawberry.UNSET
    youtube: Optional[str] = strawberry.UNSET
    thumbnail: Optional[str] = strawberry.UNSET


@strawberry_django.input(models.Song)
class SongCreateInput:
    title: auto
    length: auto
    release_date: auto
    preview: auto


@strawberry.input
class SongUpdateInput:
    id: strawberry.ID
    title: Optional[str] = strawberry.UNSET
    length: Optional[int] = strawberry.UNSET
    release_date: Optional[str] = strawberry.UNSET
    preview: Optional[str] = strawberry.UNSET


@strawberry_django.input(models.Project)
class ProjectCreateInput:
    title: auto
    number_of_songs: auto
    release_date: auto
    project_type: auto
    length: auto


@strawberry.input
class ProjectUpdateInput:
    id: strawberry.ID
    title: Optional[str] = strawberry.UNSET
    number_of_songs: Optional[int] = strawberry.UNSET
    release_date: Optional[str] = strawberry.UNSET
    project_type: Optional[str] = strawberry.UNSET
    length: Optional[int] = strawberry.UNSET


@strawberry_django.input(models.Podcast)
class PodcastCreateInput:
    title: auto
    description: auto
    since: auto
    website: auto


@strawberry.input
class PodcastUpdateInput:
    id: strawberry.ID
    title: Optional[str] = strawberry.UNSET
    description: Optional[str] = strawberry.UNSET
    since: Optional[str] = strawberry.UNSET
    website: Optional[str] = strawberry.UNSET


@strawberry_django.input(models.Outfit)
class OutfitCreateInput:
    artist_id: strawberry.ID
    description: auto
    date: auto
    preview_picture: auto
    instagram_post: auto


@strawberry.input
class OutfitUpdateInput:
    id: strawberry.ID
    artist_id: Optional[strawberry.ID] = strawberry.UNSET
    description: Optional[str] = strawberry.UNSET
    date: Optional[str] = strawberry.UNSET
    preview_picture: Optional[str] = strawberry.UNSET
    instagram_post: Optional[str] = strawberry.UNSET


@strawberry.input
class ProfileUpdateInput:
    id: strawberry.ID
    bio: Optional[str] = strawberry.UNSET
    pronouns: Optional[str] = strawberry.UNSET
    banner_picture: Optional[str] = strawberry.UNSET
    profile_picture: Optional[str] = strawberry.UNSET
    accent_color_hex: Optional[str] = strawberry.UNSET


@strawberry.input
class UserCreateInput:
    username: str
    password: str
    email: Optional[str] = None
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


@strawberry.type
class Mutation:
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
    create_sub_review: types.SubReview = strawberry_django.mutations.create(SubReviewCreateInput)
    update_sub_review: types.SubReview = strawberry_django.mutations.update(SubReviewUpdateInput)
    delete_sub_review: types.SubReview = strawberry_django.mutations.delete(strawberry.ID)

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

    create_song_artist: types.SongArtist = strawberry_django.mutations.create(SongArtistCreateInput)
    create_project_artist: types.ProjectArtist = strawberry_django.mutations.create(ProjectArtistCreateInput)
    create_project_song: types.ProjectSong = strawberry_django.mutations.create(ProjectSongCreateInput)

    @strawberry.mutation
    def create_user(self, data: UserCreateInput) -> types.User:
        user = User.objects.create_user(
            username=data.username,
            password=data.password,
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
        )
        models.Profile.objects.create(user=user)
        return user

    # --- UPDATED CUSTOM MUTATION ---
    @strawberry.mutation
    async def add_review_to_project(
            self,
            info,
            project_id: strawberry.ID,
            user_id: strawberry.ID,
            data: ReviewDataInput
    ) -> types.Review:
        """
        Custom mutation to create a review and link it to a specific project.
        This is now async to be compatible with the ASGI server.
        """
        # Wrap synchronous database calls in sync_to_async
        project = await sync_to_async(models.Project.objects.get)(pk=project_id)
        user = await sync_to_async(User.objects.get)(pk=user_id)

        review = await sync_to_async(models.Review.objects.create)(
            user=user,
            stars=data.stars,
            text=data.text,
            content_object=project  # This handles the GenericForeignKey
        )
        return review
