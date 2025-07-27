# graphql/types.py

import strawberry
from strawberry import auto
import strawberry_django
from asgiref.sync import sync_to_async

from STARS import models

@strawberry_django.type(models.Artist)
class Artist:
    id: auto
    name: auto
    picture: auto
    bio: auto
    wikipedia: auto
    pronouns: auto
    birthdate: auto
    origin: auto
    website: auto
    facebook: auto
    instagram: auto
    twitter: auto
    youtube_channel: auto
    spotify: auto
    apple_music: auto
    youtube_music: auto
    tidal: auto
    deezer: auto
    soundcloud: auto
    bandcamp: auto
    is_featured: auto

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
    id: auto
    name: auto
    description: auto
    is_featured: auto

    @strawberry.field
    async def events(self) -> list["Event"]:
        return await sync_to_async(list)(self.events.all())


@strawberry_django.type(models.Event)
class Event:
    id: auto
    name: auto
    date: auto
    location: auto
    is_one_time: auto
    reviews_count: auto
    star_average: auto
    is_featured: auto
    series: "EventSeries"

    @strawberry.field
    async def reviews(self) -> list["Review"]:
        return await sync_to_async(list)(self.reviews.all())

    @strawberry.field
    async def outfits(self) -> list["Outfit"]:
        return await sync_to_async(list)(self.outfits.all())


@strawberry_django.type(models.User)
class User:
    id: auto
    username: auto
    email: auto
    first_name: auto
    last_name: auto
    profile: "Profile"

    @strawberry.field
    async def conversations(self) -> list["Conversation"]:
        return await sync_to_async(list)(self.conversations.all())

    @strawberry.field
    async def reviews(self) -> list["Review"]:
        return await sync_to_async(list)(self.reviews.all())


@strawberry_django.type(models.Review)
class Review:
    id: auto
    stars: auto
    text: auto
    date_created: auto
    date_updated: auto
    is_latest: auto
    user: "User"
    content_object: "Reviewable"

    @strawberry.field
    async def subreviews(self) -> list["SubReview"]:
        return await sync_to_async(list)(self.subreviews.all())


@strawberry_django.type(models.SubReview)
class SubReview:
    id: auto
    topic: auto
    text: auto
    stars: auto
    review: "Review"


@strawberry_django.type(models.Project)
class Project:
    id: auto
    title: auto
    number_of_songs: auto
    release_date: auto
    project_type: models.Project.ProjectType
    length: auto
    reviews_count: auto
    star_average: auto
    spotify: auto
    apple_music: auto
    youtube_music: auto
    tidal: auto
    deezer: auto
    soundcloud: auto
    bandcamp: auto
    is_featured: auto

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
    id: auto
    title: auto
    description: auto
    since: auto
    website: auto
    spotify: auto
    apple_podcasts: auto
    youtube: auto
    youtube_music: auto
    reviews_count: auto
    star_average: auto
    is_featured: auto

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
    id: auto
    image: auto
    reviews_count: auto
    star_average: auto
    is_featured: auto
    content_object: "Coverable"

    @strawberry.field
    async def reviews(self) -> list["Review"]:
        return await sync_to_async(list)(self.reviews.all())


@strawberry_django.type(models.Song)
class Song:
    id: auto
    title: auto
    length: auto
    preview: auto
    release_date: auto
    reviews_count: auto
    star_average: auto
    is_featured: auto

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
    id: auto
    title: auto
    release_date: auto
    youtube: auto
    thumbnail: auto
    reviews_count: auto
    star_average: auto
    is_featured: auto

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
    id: auto
    description: auto
    date: auto
    preview_picture: auto
    instagram_post: auto
    reviews_count: auto
    star_average: auto
    is_featured: auto
    artist: "Artist"

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
    id: auto
    position: auto
    song: "Song"
    artist: "Artist"

@strawberry_django.type(models.ProjectArtist)
class ProjectArtist:
    id: auto
    position: auto
    project: "Project"
    artist: "Artist"

@strawberry_django.type(models.ProjectSong)
class ProjectSong:
    id: auto
    position: auto
    project: "Project"
    song: "Song"

@strawberry_django.type(models.Message)
class Message:
    id: auto
    text: auto
    time: auto
    is_pending: auto
    is_delivered: auto
    is_read: auto
    conversation: "Conversation"
    sender: "User"
    replying_to: "Message"

    @strawberry.field
    async def liked_by(self) -> list["User"]:
        return await sync_to_async(list)(self.liked_by.all())


@strawberry_django.type(models.Conversation)
class Conversation:
    id: auto
    latest_message_text: auto
    latest_message_time: auto
    latest_message: "Message"
    latest_message_sender: "User"

    @strawberry.field
    async def participants(self) -> list["User"]:
        return await sync_to_async(list)(self.participants.all())

    @strawberry.field
    async def messages(self) -> list["Message"]:
        return await sync_to_async(list)(self.messages.all())


@strawberry_django.type(models.Profile)
class Profile:
    id: auto
    banner_picture: auto
    profile_picture: auto
    bio: auto
    pronouns: auto
    accent_color_hex: auto
    followers_count: auto
    following_count: auto
    reviews_count: auto
    project_reviews_count: auto
    song_reviews_count: auto
    music_video_reviews_count: auto
    cover_reviews_count: auto
    podcast_reviews_count: auto
    outfit_reviews_count: auto
    user: "User"

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