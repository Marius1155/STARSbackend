import strawberry
from strawberry import auto
import strawberry_django
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
    song_artists: list["SongArtist"]
    project_artists: list["ProjectArtist"]
    outfits: list["Outfit"]
    podcasts: list["Podcast"]

@strawberry_django.type(models.EventSeries)
class EventSeries:
    id: auto
    name: auto
    description: auto
    is_featured: auto
    events: list["Event"]

@strawberry_django.type(models.Event)
class Event:
    id: auto
    series: auto
    name: auto
    date: auto
    location: auto
    is_one_time: auto
    reviews_count: auto
    star_average: auto
    is_featured: auto
    reviews: list["Review"]
    outfits: list["Outfit"]

@strawberry_django.type(models.User)
class User:
    id: auto
    username: auto
    email: auto
    first_name: auto
    last_name: auto
    profile: auto
    conversations: list["Conversation"]
    reviews: list["Review"]

@strawberry_django.type(models.Review)
class Review:
    id: auto
    stars: auto
    text: auto
    user: auto
    date_created: auto
    date_updated: auto
    is_latest: auto
    content_object: "Reviewable"
    subreviews: list["SubReview"]

@strawberry_django.type(models.SubReview)
class SubReview:
    id: auto
    review: auto
    topic: auto
    text: auto
    stars: auto

@strawberry_django.type(models.Project)
class Project:
    id: auto
    title: auto
    number_of_songs: auto
    release_date: auto
    project_type: auto
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
    covers: list["Cover"]
    reviews: list["Review"]
    alternative_versions: list["Project"]
    project_songs: list["ProjectSong"]
    project_artists: list["ProjectArtist"]

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
    hosts: list["Artist"]
    covers: list["Cover"]
    reviews: list["Review"]

@strawberry_django.type(models.Cover)
class Cover:
    id: auto
    image: auto
    reviews_count: auto
    star_average: auto
    is_featured: auto
    content_object: "Coverable"
    reviews: list["Review"]

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
    reviews: list["Review"]
    alternative_versions: list["Song"]
    song_artists: list["SongArtist"]
    project_songs: list["ProjectSong"]
    music_videos: list["MusicVideo"]

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
    songs: list["Song"]
    reviews: list["Review"]
    outfits: list["Outfit"]

@strawberry_django.type(models.Outfit)
class Outfit:
    id: auto
    artist: auto
    description: auto
    date: auto
    preview_picture: auto
    instagram_post: auto
    reviews_count: auto
    star_average: auto
    is_featured: auto
    events: list["Event"]
    music_videos: list["MusicVideo"]
    covers: list["Cover"]
    reviews: list["Review"]
    matches: list["Outfit"]

@strawberry_django.type(models.SongArtist)
class SongArtist:
    id: auto
    song: auto
    artist: auto
    position: auto

@strawberry_django.type(models.ProjectArtist)
class ProjectArtist:
    id: auto
    project: auto
    artist: auto
    position: auto

@strawberry_django.type(models.ProjectSong)
class ProjectSong:
    id: auto
    project: auto
    song: auto
    position: auto

@strawberry_django.type(models.Message)
class Message:
    id: auto
    conversation: auto
    sender: auto
    text: auto
    time: auto
    is_pending: auto
    is_delivered: auto
    is_read: auto
    replying_to: auto
    liked_by: list["User"]

@strawberry_django.type(models.Conversation)
class Conversation:
    id: auto
    latest_message: auto
    latest_message_text: auto
    latest_message_time: auto
    latest_message_sender: auto
    participants: list["User"]
    messages: list["Message"]

@strawberry_django.type(models.Profile)
class Profile:
    id: auto
    user: auto
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
    followers: list["Profile"]
    following: list["Profile"]

Reviewable = strawberry.union(
    "Reviewable",
    (Event, Project, Song, MusicVideo, Podcast, Outfit, Cover),
)

Coverable = strawberry.union(
    "Coverable",
    (Project, Podcast),
)