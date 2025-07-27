# graphql/types.py

import strawberry
import strawberry_django
from asgiref.sync import sync_to_async

from STARS import models

@strawberry_django.type(models.Artist)
class Artist:
    id: strawberry_django.auto
    name: strawberry_django.auto
    picture: strawberry_django.auto
    bio: strawberry_django.auto
    wikipedia: strawberry_django.auto
    pronouns: strawberry_django.auto
    birthdate: strawberry_django.auto
    origin: strawberry_django.auto
    website: strawberry_django.auto
    facebook: strawberry_django.auto
    instagram: strawberry_django.auto
    twitter: strawberry_django.auto
    youtube_channel: strawberry_django.auto
    spotify: strawberry_django.auto
    apple_music: strawberry_django.auto
    youtube_music: strawberry_django.auto
    tidal: strawberry_django.auto
    deezer: strawberry_django.auto
    soundcloud: strawberry_django.auto
    bandcamp: strawberry_django.auto
    is_featured: strawberry_django.auto

    @strawberry.field
    async def song_artists(self) -> list["SongArtist"]:
        return await sync_to_async(list)(self.song_artists.all())

    @strawberry.field
    async def project_artists(self) -> list["ProjectArtist"]:
        return await sync_to_async(list)(self.project_artists.all())

    @strawberry.field
    async def outfits(self) -> list["Outfit"]:
        return await sync_to_async(list)(self.outfits.all())

    @strawberry.field
    async def podcasts(self) -> list["Podcast"]:
        return await sync_to_async(list)(self.podcasts.all())


@strawberry_django.type(models.EventSeries)
class EventSeries:
    id: strawberry_django.auto
    name: strawberry_django.auto
    description: strawberry_django.auto
    is_featured: strawberry_django.auto

    @strawberry.field
    async def events(self) -> list["Event"]:
        return await sync_to_async(list)(self.events.all())


@strawberry_django.type(models.Event)
class Event:
    id: strawberry_django.auto
    series: strawberry_django.auto
    name: strawberry_django.auto
    date: strawberry_django.auto
    location: strawberry_django.auto
    is_one_time: strawberry_django.auto
    reviews_count: strawberry_django.auto
    star_average: strawberry_django.auto
    is_featured: strawberry_django.auto

    @strawberry.field
    async def reviews(self) -> list["Review"]:
        return await sync_to_async(list)(self.reviews.all())

    @strawberry.field
    async def outfits(self) -> list["Outfit"]:
        return await sync_to_async(list)(self.outfits.all())


@strawberry_django.type(models.User)
class User:
    id: strawberry_django.auto
    username: strawberry_django.auto
    email: strawberry_django.auto
    first_name: strawberry_django.auto
    last_name: strawberry_django.auto
    profile: strawberry_django.auto

    @strawberry.field
    async def conversations(self) -> list["Conversation"]:
        return await sync_to_async(list)(self.conversations.all())

    @strawberry.field
    async def reviews(self) -> list["Review"]:
        return await sync_to_async(list)(self.reviews.all())


@strawberry_django.type(models.Review)
class Review:
    id: strawberry_django.auto
    stars: strawberry_django.auto
    text: strawberry_django.auto
    user: strawberry_django.auto
    date_created: strawberry_django.auto
    date_updated: strawberry_django.auto
    is_latest: strawberry_django.auto
    content_object: "Reviewable"

    @strawberry.field
    async def subreviews(self) -> list["SubReview"]:
        return await sync_to_async(list)(self.subreviews.all())


@strawberry_django.type(models.SubReview)
class SubReview:
    id: strawberry_django.auto
    review: strawberry_django.auto
    topic: strawberry_django.auto
    text: strawberry_django.auto
    stars: strawberry_django.auto


@strawberry_django.type(models.Project)
class Project:
    id: strawberry_django.auto
    title: strawberry_django.auto
    number_of_songs: strawberry_django.auto
    release_date: strawberry_django.auto
    project_type: strawberry_django.auto
    length: strawberry_django.auto
    reviews_count: strawberry_django.auto
    star_average: strawberry_django.auto
    spotify: strawberry_django.auto
    apple_music: strawberry_django.auto
    youtube_music: strawberry_django.auto
    tidal: strawberry_django.auto
    deezer: strawberry_django.auto
    soundcloud: strawberry_django.auto
    bandcamp: strawberry_django.auto
    is_featured: strawberry_django.auto

    @strawberry.field
    async def covers(self) -> list["Cover"]:
        return await sync_to_async(list)(self.covers.all())

    @strawberry.field
    async def reviews(self) -> list["Review"]:
        return await sync_to_async(list)(self.reviews.all())

    @strawberry.field
    async def alternative_versions(self) -> list["Project"]:
        return await sync_to_async(list)(self.alternative_versions.all())

    @strawberry.field
    async def project_songs(self) -> list["ProjectSong"]:
        return await sync_to_async(list)(self.project_songs.all())

    @strawberry.field
    async def project_artists(self) -> list["ProjectArtist"]:
        return await sync_to_async(list)(self.project_artists.all())


@strawberry_django.type(models.Podcast)
class Podcast:
    id: strawberry_django.auto
    title: strawberry_django.auto
    description: strawberry_django.auto
    since: strawberry_django.auto
    website: strawberry_django.auto
    spotify: strawberry_django.auto
    apple_podcasts: strawberry_django.auto
    youtube: strawberry_django.auto
    youtube_music: strawberry_django.auto
    reviews_count: strawberry_django.auto
    star_average: strawberry_django.auto
    is_featured: strawberry_django.auto

    @strawberry.field
    async def hosts(self) -> list["Artist"]:
        return await sync_to_async(list)(self.hosts.all())

    @strawberry.field
    async def covers(self) -> list["Cover"]:
        return await sync_to_async(list)(self.covers.all())

    @strawberry.field
    async def reviews(self) -> list["Review"]:
        return await sync_to_async(list)(self.reviews.all())


@strawberry_django.type(models.Cover)
class Cover:
    id: strawberry_django.auto
    image: strawberry_django.auto
    reviews_count: strawberry_django.auto
    star_average: strawberry_django.auto
    is_featured: strawberry_django.auto
    content_object: "Coverable"

    @strawberry.field
    async def reviews(self) -> list["Review"]:
        return await sync_to_async(list)(self.reviews.all())


@strawberry_django.type(models.Song)
class Song:
    id: strawberry_django.auto
    title: strawberry_django.auto
    length: strawberry_django.auto
    preview: strawberry_django.auto
    release_date: strawberry_django.auto
    reviews_count: strawberry_django.auto
    star_average: strawberry_django.auto
    is_featured: strawberry_django.auto

    @strawberry.field
    async def reviews(self) -> list["Review"]:
        return await sync_to_async(list)(self.reviews.all())

    @strawberry.field
    async def alternative_versions(self) -> list["Song"]:
        return await sync_to_async(list)(self.alternative_versions.all())

    @strawberry.field
    async def song_artists(self) -> list["SongArtist"]:
        return await sync_to_async(list)(self.song_artists.all())

    @strawberry.field
    async def project_songs(self) -> list["ProjectSong"]:
        return await sync_to_async(list)(self.project_songs.all())

    @strawberry.field
    async def music_videos(self) -> list["MusicVideo"]:
        return await sync_to_async(list)(self.music_videos.all())


@strawberry_django.type(models.MusicVideo)
class MusicVideo:
    id: strawberry_django.auto
    title: strawberry_django.auto
    release_date: strawberry_django.auto
    youtube: strawberry_django.auto
    thumbnail: strawberry_django.auto
    reviews_count: strawberry_django.auto
    star_average: strawberry_django.auto
    is_featured: strawberry_django.auto

    @strawberry.field
    async def songs(self) -> list["Song"]:
        return await sync_to_async(list)(self.songs.all())

    @strawberry.field
    async def reviews(self) -> list["Review"]:
        return await sync_to_async(list)(self.reviews.all())

    @strawberry.field
    async def outfits(self) -> list["Outfit"]:
        return await sync_to_async(list)(self.outfits.all())


@strawberry_django.type(models.Outfit)
class Outfit:
    id: strawberry_django.auto
    artist: strawberry_django.auto
    description: strawberry_django.auto
    date: strawberry_django.auto
    preview_picture: strawberry_django.auto
    instagram_post: strawberry_django.auto
    reviews_count: strawberry_django.auto
    star_average: strawberry_django.auto
    is_featured: strawberry_django.auto

    @strawberry.field
    async def events(self) -> list["Event"]:
        return await sync_to_async(list)(self.events.all())

    @strawberry.field
    async def music_videos(self) -> list["MusicVideo"]:
        return await sync_to_async(list)(self.music_videos.all())

    @strawberry.field
    async def covers(self) -> list["Cover"]:
        return await sync_to_async(list)(self.covers.all())

    @strawberry.field
    async def reviews(self) -> list["Review"]:
        return await sync_to_async(list)(self.reviews.all())

    @strawberry.field
    async def matches(self) -> list["Outfit"]:
        return await sync_to_async(list)(self.matches.all())


@strawberry_django.type(models.SongArtist)
class SongArtist:
    id: strawberry_django.auto
    song: strawberry_django.auto
    artist: strawberry_django.auto
    position: strawberry_django.auto


@strawberry_django.type(models.ProjectArtist)
class ProjectArtist:
    id: strawberry_django.auto
    project: strawberry_django.auto
    artist: strawberry_django.auto
    position: strawberry_django.auto


@strawberry_django.type(models.ProjectSong)
class ProjectSong:
    id: strawberry_django.auto
    project: strawberry_django.auto
    song: strawberry_django.auto
    position: strawberry_django.auto


@strawberry_django.type(models.Message)
class Message:
    id: strawberry_django.auto
    conversation: strawberry_django.auto
    sender: strawberry_django.auto
    text: strawberry_django.auto
    time: strawberry_django.auto
    is_pending: strawberry_django.auto
    is_delivered: strawberry_django.auto
    is_read: strawberry_django.auto
    replying_to: strawberry_django.auto

    @strawberry.field
    async def liked_by(self) -> list["User"]:
        return await sync_to_async(list)(self.liked_by.all())


@strawberry_django.type(models.Conversation)
class Conversation:
    id: strawberry_django.auto
    latest_message: strawberry_django.auto
    latest_message_text: strawberry_django.auto
    latest_message_time: strawberry_django.auto
    latest_message_sender: strawberry_django.auto

    @strawberry.field
    async def participants(self) -> list["User"]:
        return await sync_to_async(list)(self.participants.all())

    @strawberry.field
    async def messages(self) -> list["Message"]:
        return await sync_to_async(list)(self.messages.all())


@strawberry_django.type(models.Profile)
class Profile:
    id: strawberry_django.auto
    user: strawberry_django.auto
    banner_picture: strawberry_django.auto
    profile_picture: strawberry_django.auto
    bio: strawberry_django.auto
    pronouns: strawberry_django.auto
    accent_color_hex: strawberry_django.auto
    followers_count: strawberry_django.auto
    following_count: strawberry_django.auto
    reviews_count: strawberry_django.auto
    project_reviews_count: strawberry_django.auto
    song_reviews_count: strawberry_django.auto
    music_video_reviews_count: strawberry_django.auto
    cover_reviews_count: strawberry_django.auto
    podcast_reviews_count: strawberry_django.auto
    outfit_reviews_count: strawberry_django.auto

    @strawberry.field
    async def followers(self) -> list["Profile"]:
        return await sync_to_async(list)(self.followers.all())

    @strawberry.field
    async def following(self) -> list["Profile"]:
        return await sync_to_async(list)(self.following.all())


Reviewable = strawberry.union(
    "Reviewable",
    (Event, Project, Song, MusicVideo, Podcast, Outfit, Cover),
    description="Represents an object that can be reviewed.",
)

Coverable = strawberry.union(
    "Coverable",
    (Project, Podcast),
    description="Represents an object that can have a cover image.",
)