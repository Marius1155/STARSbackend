
# STARS/graphql/mutations.py

import strawberry
import strawberry_django
from strawberry import auto
from typing import List
from django.contrib.auth.models import User

from STARS import models
from . import types

# -----------------------------------------------------------------------------
# Input Types
# -----------------------------------------------------------------------------
# Define "input" types for creating and updating each model.
# The `is_partial=True` argument makes all fields optional for updates.

@strawberry_django.input(models.Artist)
class ArtistCreateInput:
    name: auto
    picture: auto
    bio: auto
    wikipedia: auto
    pronouns: auto
    birthdate: auto
    origin: auto

@strawberry_django.input(models.Artist, is_partial=True)
class ArtistUpdateInput:
    id: strawberry.ID
    name: auto
    picture: auto
    bio: auto
    wikipedia: auto
    pronouns: auto
    birthdate: auto
    origin: auto

@strawberry_django.input(models.EventSeries)
class EventSeriesCreateInput:
    name: auto
    description: auto

@strawberry_django.input(models.EventSeries, is_partial=True)
class EventSeriesUpdateInput:
    id: strawberry.ID
    name: auto
    description: auto

@strawberry_django.input(models.Event)
class EventCreateInput:
    name: auto
    date: auto
    location: auto
    is_one_time: auto
    series_id: strawberry.ID | None = None

@strawberry_django.input(models.Event, is_partial=True)
class EventUpdateInput:
    id: strawberry.ID
    name: auto
    date: auto
    location: auto
    is_one_time: auto
    series_id: strawberry.ID | None = None

@strawberry_django.input(models.Review)
class ReviewCreateInput:
    user_id: strawberry.ID
    stars: auto
    text: auto
    # Note: The content_object (e.g., a Project) must be linked separately after creation.

@strawberry_django.input(models.Review, is_partial=True)
class ReviewUpdateInput:
    id: strawberry.ID
    stars: auto
    text: auto

@strawberry_django.input(models.SubReview)
class SubReviewCreateInput:
    review_id: strawberry.ID
    topic: auto
    text: auto
    stars: auto

@strawberry_django.input(models.SubReview, is_partial=True)
class SubReviewUpdateInput:
    id: strawberry.ID
    topic: auto
    text: auto
    stars: auto

@strawberry_django.input(models.MusicVideo)
class MusicVideoCreateInput:
    title: auto
    release_date: auto
    youtube: auto
    thumbnail: auto

@strawberry_django.input(models.MusicVideo, is_partial=True)
class MusicVideoUpdateInput:
    id: strawberry.ID
    title: auto
    release_date: auto
    youtube: auto
    thumbnail: auto

@strawberry_django.input(models.Song)
class SongCreateInput:
    title: auto
    length: auto
    release_date: auto
    preview: auto

@strawberry_django.input(models.Song, is_partial=True)
class SongUpdateInput:
    id: strawberry.ID
    title: auto
    length: auto
    release_date: auto
    preview: auto

@strawberry_django.input(models.Project)
class ProjectCreateInput:
    title: auto
    number_of_songs: auto
    release_date: auto
    project_type: auto
    length: auto

@strawberry_django.input(models.Project, is_partial=True)
class ProjectUpdateInput:
    id: strawberry.ID
    title: auto
    number_of_songs: auto
    release_date: auto
    project_type: auto
    length: auto

@strawberry_django.input(models.Podcast)
class PodcastCreateInput:
    title: auto
    description: auto
    since: auto
    website: auto

@strawberry_django.input(models.Podcast, is_partial=True)
class PodcastUpdateInput:
    id: strawberry.ID
    title: auto
    description: auto
    since: auto
    website: auto

@strawberry_django.input(models.Outfit)
class OutfitCreateInput:
    artist_id: strawberry.ID
    description: auto
    date: auto
    preview_picture: auto
    instagram_post: auto

@strawberry_django.input(models.Outfit, is_partial=True)
class OutfitUpdateInput:
    id: strawberry.ID
    artist_id: strawberry.ID
    description: auto
    date: auto
    preview_picture: auto
    instagram_post: auto

@strawberry_django.input(models.Profile, is_partial=True)
class ProfileUpdateInput:
    id: strawberry.ID
    bio: auto
    pronouns: auto
    banner_picture: auto
    profile_picture: auto
    accent_color_hex: auto

# Custom input for creating a user to handle the password securely.
@strawberry.input
class UserCreateInput:
    username: str
    password: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None

# -----------------------------------------------------------------------------
# Relationship Input Types
# -----------------------------------------------------------------------------

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

# -----------------------------------------------------------------------------
# Mutation Class
# -----------------------------------------------------------------------------

@strawberry.type
class Mutation:
    # --- Artist Mutations ---
    create_artist: types.Artist = strawberry_django.mutations.create(ArtistCreateInput)
    update_artist: types.Artist = strawberry_django.mutations.update(ArtistUpdateInput)
    delete_artist: types.Artist = strawberry_django.mutations.delete(strawberry.ID)

    # --- Project Mutations ---
    create_project: types.Project = strawberry_django.mutations.create(ProjectCreateInput)
    update_project: types.Project = strawberry_django.mutations.update(ProjectUpdateInput)
    delete_project: types.Project = strawberry_django.mutations.delete(strawberry.ID)

    # --- Song Mutations ---
    create_song: types.Song = strawberry_django.mutations.create(SongCreateInput)
    update_song: types.Song = strawberry_django.mutations.update(SongUpdateInput)
    delete_song: types.Song = strawberry_django.mutations.delete(strawberry.ID)

    # --- Event & Series Mutations ---
    create_event_series: types.EventSeries = strawberry_django.mutations.create(EventSeriesCreateInput)
    update_event_series: types.EventSeries = strawberry_django.mutations.update(EventSeriesUpdateInput)
    delete_event_series: types.EventSeries = strawberry_django.mutations.delete(strawberry.ID)
    create_event: types.Event = strawberry_django.mutations.create(EventCreateInput)
    update_event: types.Event = strawberry_django.mutations.update(EventUpdateInput)
    delete_event: types.Event = strawberry_django.mutations.delete(strawberry.ID)

    # --- Review & SubReview Mutations ---
    create_review: types.Review = strawberry_django.mutations.create(ReviewCreateInput)
    update_review: types.Review = strawberry_django.mutations.update(ReviewUpdateInput)
    delete_review: types.Review = strawberry_django.mutations.delete(strawberry.ID)
    create_sub_review: types.SubReview = strawberry_django.mutations.create(SubReviewCreateInput)
    update_sub_review: types.SubReview = strawberry_django.mutations.update(SubReviewUpdateInput)
    delete_sub_review: types.SubReview = strawberry_django.mutations.delete(strawberry.ID)

    # --- MusicVideo, Podcast, Outfit Mutations ---
    create_music_video: types.MusicVideo = strawberry_django.mutations.create(MusicVideoCreateInput)
    update_music_video: types.MusicVideo = strawberry_django.mutations.update(MusicVideoUpdateInput)
    delete_music_video: types.MusicVideo = strawberry_django.mutations.delete(strawberry.ID)
    create_podcast: types.Podcast = strawberry_django.mutations.create(PodcastCreateInput)
    update_podcast: types.Podcast = strawberry_django.mutations.update(PodcastUpdateInput)
    delete_podcast: types.Podcast = strawberry_django.mutations.delete(strawberry.ID)
    create_outfit: types.Outfit = strawberry_django.mutations.create(OutfitCreateInput)
    update_outfit: types.Outfit = strawberry_django.mutations.update(OutfitUpdateInput)
    delete_outfit: types.Outfit = strawberry_django.mutations.delete(strawberry.ID)

    # --- Profile Mutation ---
    update_profile: types.Profile = strawberry_django.mutations.update(ProfileUpdateInput)

    # --- Relationship Mutations ---
    create_song_artist: types.SongArtist = strawberry_django.mutations.create(SongArtistCreateInput)
    create_project_artist: types.ProjectArtist = strawberry_django.mutations.create(ProjectArtistCreateInput)
    create_project_song: types.ProjectSong = strawberry_django.mutations.create(ProjectSongCreateInput)

    # --- User Creation (Custom) ---
    @strawberry.mutation
    def create_user(self, data: UserCreateInput) -> types.User:
        """
        Custom mutation to create a new user and securely hash the password.
        """
        user = User.objects.create_user(
            username=data.username,
            password=data.password,
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
        )
        # Create a profile for the new user
        models.Profile.objects.create(user=user)
        return user

