import strawberry_django
from strawberry import auto

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
    series: "EventSeries"
    name: auto
    date: auto
    location: auto
    is_one_time: auto
    reviews_count: auto
    reviews: list["Review"]
    star_average: auto
    is_featured: auto
    outfits: list["Outfit"]

@strawberry_django.type(models.Review)
class Review:
    id: auto
    stars: auto
    text: auto
    user: "User"
    date_created: auto
    date_updated: auto
    is_latest: auto

    subreviews: list["SubReview"]
    '''
    ===content type stuff===
    
    podcasts: list["Podcast"]
    outfits: list["Outfit"]
    projects: list["Project"]
    songs: list["Song"]
    covers: list["Cover"]
    music_videos: list["MusicVideo"]
    events: list["Event"]'''

@strawberry_django.type(models.SubReview)
class SubReview:
    id: auto
    review: "Review"
    topic: auto
    text: auto
    stars: auto

@strawberry_django.type(models.Cover)
class Cover:
    id: auto
    image: auto

    '''
    ===content type stuff===
    
    projects: list["Project"]
    podcasts: list["Podcast"]'''

    reviews_count: auto
    reviews: list["Review"]
    star_average: auto
    is_featured: auto

@strawberry_django.type(models.MusicVideo)
class MusicVideo:
    id: auto
    title: auto
    songs: list["Song"]
    release_date: auto
    youtube: auto
    thumbnail: auto
    reviews_count: auto
    reviews: list["Review"]
    star_average: auto
    is_featured: auto
    outfits: list["Outfit"]

@strawberry_django.type(models.Song)
class Song:
    id: auto
    title: auto
    length: auto
    preview: auto
    release_date: auto
    reviews_count: auto
    reviews: list["Review"]
    star_average: auto
    alternative_versions: list["Song"]
    is_featured: auto
    song_artists: list["SongArtist"]
    project_songs: list["ProjectSong"]

@strawberry_django.type(models.SongArtist)
class SongArtist:
    id: auto
    song: "Song"
    artist: "Artist"
    position: auto

@strawberry_django.type(models.Project)
class Project:
    id: auto
    title: auto
    number_of_songs: auto
    release_date: auto
    type: auto
    covers: list["Cover"]
    length: auto
    reviews: list["Review"]
    reviews_count: auto
    star_average: auto
    alternative_versions: list["Project"]
    spotify: auto
    apple_music: auto
    youtube_music: auto
    tidal: auto
    deezer: auto
    soundcloud: auto
    bandcamp: auto
    is_featured: auto
    project_songs: list["ProjectSong"]
    project_artists: list["ProjectArtist"]

@strawberry_django.type(models.ProjectArtist)
class ProjectArtist:
    id: auto
    project: "Project"
    artist: "Artist"
    position: auto

@strawberry_django.type(models.ProjectSong)
class ProjectSong:
    id: auto
    project: "Project"
    song: "Song"
    position: auto

@strawberry_django.type(models.Podcast)
class Podcast:
    id: auto
    title: auto
    hosts: list["Artist"]
    description: auto
    since: auto
    covers: list["Cover"]
    website: auto
    spotify: auto
    apple_podcasts: auto
    youtube: auto
    youtube_music: auto
    reviews_count: auto
    reviews: list["Review"]
    star_average: auto
    is_featured: auto

@strawberry_django.type(models.Outfit)
class Outfit:
    id: auto
    artist: "Artist"
    description: auto
    date: auto
    events: list["Event"]
    music_videos: list["MusicVideo"]
    covers: list["Cover"]
    preview_picture: auto
    instagram_post: auto
    reviews_count: auto
    reviews: list["Review"]
    star_average: auto
    matches: list["Outfit"]
    is_featured: auto

@strawberry_django.type(models.Conversation)
class Conversation:
    id: auto
    participants: list["User"]
    latest_message: "Message"
    latest_message_text: auto
    latest_message_time: auto
    latest_message_sender: "User"
    messages: list["Message"]

@strawberry_django.type(models.Message)
class Message:
    id: auto
    conversation: "Conversation"
    sender: "User"
    text: auto
    time: auto
    is_pending: auto
    is_delivered: auto
    is_read: auto
    liked_by: list["User"]
    replying_to: "Message"

@strawberry_django.type(models.Profile)
class Profile:
    id: auto
    user: "User"
    banner_picture: auto
    profile_picture: auto
    bio: auto
    pronouns: auto
    accent_color_hex: auto

    followers_count: auto
    following_count: auto
    followers: list["User"]
    following: list["User"]

    reviews_count: auto
    project_reviews_count: auto
    song_reviews_count: auto
    music_video_reviews_count: auto
    cover_reviews_count: auto
    podcast_reviews_count: auto
    outfit_reviews_count: auto

    reviews: list["Review"]

@strawberry_django.type(models.User)
class User:
    id: auto
    username: auto
    email: auto
    first_name: auto
    last_name: auto
    profile: "Profile"
    conversations: list["Conversation"]
    reviews: list["Review"]


