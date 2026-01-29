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
import enum
from datetime import datetime
from .subscriptions import broadcast_conversation_update, broadcast_message_event
from ..services.itunes import iTunesService  # Ensure this service exists from previous step
from dateutil import parser
import asyncio
import colorsys



# --- IMPORTS FOR SOCIAL LOGIN ---
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialApp, SocialLogin, SocialToken

from . import types

import base64
import tempfile
import cloudinary.uploader
from django.db import transaction
from STARS import models
from ..services.apple_music import AppleMusicService

def get_high_res_artwork(url: str) -> str:
    if not url: return ""
    return re.sub(r"\d+x\d+bb", "3000x3000bb", url)

ITUNES_GENRES = {
    1301: "Arts", 1303: "Comedy", 1304: "Education", 1305: "Kids & Family",
    1309: "TV & Film", 1310: "Music", 1311: "News", 1314: "Religion",
    1315: "Science", 1316: "Sports", 1318: "Technology", 1321: "Business",
    1323: "Games", 1324: "Society", 1325: "Government", 1482: "Health",
    1483: "Design", 1484: "Automotive", 1485: "Performing Arts",
    1486: "Visual Arts", 1487: "Fashion", 1488: "True Crime",
    1511: "Fiction", 1512: "History"
}


def ensure_muted_color(hex_color: str, max_saturation: float = 0.5) -> str:
    """
    Parses a hex color, converts to HLS, and caps the saturation.
    Returns the modified hex string.
    """
    if not hex_color:
        return None

    # 1. Clean the hex string
    hex_clean = hex_color.lstrip('#')
    if len(hex_clean) != 6:
        return hex_color  # Return original if malformed

    # 2. Convert Hex to RGB (0-1 range)
    r = int(hex_clean[0:2], 16) / 255.0
    g = int(hex_clean[2:4], 16) / 255.0
    b = int(hex_clean[4:6], 16) / 255.0

    # 3. Convert RGB to HLS (Hue, Lightness, Saturation)
    h, l, s = colorsys.rgb_to_hls(r, g, b)

    # 4. "Add Gray" / Desaturate
    # If the color is more vibrant than our limit, we clamp it down.
    if s > max_saturation:
        s = max_saturation

        # 5. Convert back to RGB
    r_new, g_new, b_new = colorsys.hls_to_rgb(h, l, s)

    # 6. Convert back to Hex
    def to_int(val):
        return max(0, min(255, int(val * 255)))

    return f"#{to_int(r_new):02x}{to_int(g_new):02x}{to_int(b_new):02x}"


def process_image_from_url(image_url: str):
    """
    Downloads image from a URL, uploads to Cloudinary, extracts colors,
    and mutes them if they are too vibrant.
    Returns: (secure_url, primary_color, secondary_color)
    """
    if not image_url:
        return None, None, None

    # Apple Music URLs often come as '.../100x100bb.jpg' or with placeholders '{w}x{h}'
    if "{w}" in image_url and "{h}" in image_url:
        final_url = image_url.replace("{w}", "1024").replace("{h}", "1024")
    else:
        final_url = image_url

    try:
        response = requests.get(final_url, stream=True)
        if response.status_code != 200:
            return None, None, None

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            for chunk in response.iter_content(chunk_size=4096):
                temp_file.write(chunk)
            temp_file.flush()

            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(temp_file.name, colors=True)

        os.unlink(temp_file.name)

        url = upload_result.get("secure_url")
        raw_colors = upload_result.get("colors", [])

        # Get raw hex colors
        raw_primary = raw_colors[0][0] if len(raw_colors) > 0 else None
        raw_secondary = raw_colors[1][0] if len(raw_colors) > 1 else None

        # --- THE MAGIC HAPPENS HERE ---
        # We process the colors to ensure they aren't eye-straining.
        # 0.5 to 0.6 is usually a good "comfortable" saturation limit.
        primary = ensure_muted_color(raw_primary, max_saturation=0.55)
        secondary = ensure_muted_color(raw_secondary, max_saturation=0.55)

        return url, primary, secondary

    except Exception as e:
        print(f"Error processing image: {e}")
        return None, None, None


def get_or_create_project_genres(genre_names: List[str], project: types.Project):
    if not genre_names:
        return

    i = 1
    for name in genre_names:
        if name != "Music":
            genre_obj, _ = models.MusicGenre.objects.get_or_create(title=name)
            models.ProjectGenresOrdered.objects.create(
                project=project,
                genre=genre_obj,
                position=i
            )
            i += 1


def get_or_create_song_genres(genre_names: List[str], song: types.Song):
    if not genre_names:
        return

    i = 1
    for name in genre_names:
        if name != "Music":
            genre_obj, _ = models.MusicGenre.objects.get_or_create(title=name)
            models.SongGenresOrdered.objects.create(
                song=song,
                genre=genre_obj,
                position=i
            )
            i += 1


def get_or_create_artist_genres(genre_names: List[str], artist: types.Artist):
    if not genre_names:
        return

    i = 1
    for name in genre_names:
        if name != "Music":
            genre_obj, _ = models.MusicGenre.objects.get_or_create(title=name)
            models.ArtistGenresOrdered.objects.create(
                artist=artist,
                genre=genre_obj,
                position=i
            )
            i += 1


def get_or_create_podcast_genres(genre_names: List[str], podcast: types.Podcast):
    if not genre_names:
        return

    i = 1
    for name in genre_names:
        if name != "Podcasts":
            genre_obj, _ = models.PodcastGenre.objects.get_or_create(title=name)
            models.PodcastGenresOrdered.objects.create(
                podcast=podcast,
                genre=genre_obj,
                position=i
            )
            i += 1




@strawberry.input
class MusicVideoInput:
    youtube_id: str
    title: str
    thumbnail_url: str
    channel_name: str
    published_at: datetime
    length_ms: int
    youtube_url: str
    songs_ids: list[strawberry.ID]


@strawberry.input
class MusicVideoUpdateInput:
    id: strawberry.ID
    title: Optional[str] = strawberry.UNSET
    release_date: Optional[str] = strawberry.UNSET
    youtube: Optional[str] = strawberry.UNSET
    thumbnail: Optional[str] = strawberry.UNSET
    is_featured: Optional[bool] = strawberry.UNSET
    featured_message: Optional[str] = strawberry.UNSET


@strawberry.input
class PerformanceVideoInput:
    youtube_id: str
    title: str
    thumbnail_url: str
    channel_name: str
    published_at: datetime
    length_ms: int
    youtube_url: str
    artists_apple_music_ids: list[strawberry.ID]
    songs_ids: list[strawberry.ID]
    event_id: Optional[str]
    event_name: Optional[str]
    event_date: Optional[datetime]
    event_type: Optional[str]
    event_location: Optional[str]
    event_series_id: Optional[str]
    event_series_name: Optional[str]


@strawberry.input
class PerformanceVideoUpdateInput:
    id: strawberry.ID
    title: Optional[str] = strawberry.UNSET
    release_date: Optional[str] = strawberry.UNSET
    youtube: Optional[str] = strawberry.UNSET
    thumbnail: Optional[str] = strawberry.UNSET
    is_featured: Optional[bool] = strawberry.UNSET
    featured_message: Optional[str] = strawberry.UNSET


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
class ProjectUpdateInput:
    id: strawberry.ID
    apple_music_id: Optional[str] = strawberry.UNSET
    title: Optional[str] = strawberry.UNSET
    number_of_songs: Optional[int] = strawberry.UNSET
    release_date: Optional[str] = strawberry.UNSET
    project_type: Optional[str] = strawberry.UNSET
    record_label: Optional[str] = strawberry.UNSET
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
    disc_number: auto


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
    DISLIKE = "dislike"


@strawberry_django.input(models.SearchHistory)
class SearchHistoryCreateInput:
    query: str
    category: str


MARINA_AND_THE_DIAMONDS_ID = "306359292"
MARINA_ID = "1451242169"

# Helper to swap IDs in a list or single string
def _prepare_am_ids(ids: Optional[List[strawberry.ID]]) -> List[strawberry.ID]:
    if not ids:
        return []
    return [MARINA_ID if am_id == MARINA_AND_THE_DIAMONDS_ID else am_id for am_id in ids]

def _format_list_to_string(items: List[str]) -> str:
    """Converts ['A', 'B', 'C'] to 'A, B & C'."""
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return f"{', '.join(items[:-1])} & {items[-1]}"

async def _fetch_missing_artist_data(am_ids: set, am_service) -> dict:
    artists_data = {}
    for am_id in am_ids:
        exists = await sync_to_async(models.Artist.objects.filter(apple_music_id=am_id).exists)()
        if exists: continue
        try:
            artist_json = await am_service.get_artist(f"/v1/catalog/us/artists/{am_id}")
            attrs = artist_json.get("attributes", {})
            pic_url, primary, secondary = await sync_to_async(process_image_from_url)(attrs.get("artwork", {}).get("url", ""))
            artists_data[am_id] = {
                "name": attrs.get("name", ""),
                "apple_music_url": attrs.get("url", ""),
                "picture": pic_url or "",
                "primary_color": primary,
                "secondary_color": secondary,
                "genres": attrs.get("genreNames", [])
            }
        except Exception: pass
    return artists_data

async def _fetch_performance_artists(am_ids: set, am_service) -> dict:
    swapped_ids = _prepare_am_ids(list(am_ids))
    return await _fetch_missing_artist_data(set(swapped_ids), am_service)

async def _process_cover(cover_url: str):
    if not cover_url: return None, None, None
    try:
        return await sync_to_async(process_image_from_url)(cover_url)
    except Exception: return None, None, None

def _create_artist_from_data(am_id: str, adata: dict) -> models.Artist:
    artist = models.Artist.objects.create(
        apple_music_id=am_id, name=adata["name"], picture=adata["picture"],
        primary_color=adata["primary_color"] or "", secondary_color=adata["secondary_color"] or "",
        apple_music=adata["apple_music_url"]
    )
    if adata["genres"]: get_or_create_artist_genres(adata["genres"], artist)
    return artist

def _get_or_create_artist_node(am_id: str, fetched_data: dict) -> Optional[models.Artist]:
    artist = models.Artist.objects.filter(apple_music_id=am_id).first()
    if not artist and am_id in fetched_data:
        artist = _create_artist_from_data(am_id, fetched_data[am_id])
    return artist

def _determine_project_type(is_single: bool, song_count: int) -> str:
    if is_single: return models.Project.ProjectType.SINGLE
    return models.Project.ProjectType.EP if song_count <= 6 else models.Project.ProjectType.ALBUM

def _link_artists_to_song(song_obj, am_ids: List[str], get_artist_fn):
    unique_ids = list(dict.fromkeys(am_ids))
    for j, s_am_id in enumerate(unique_ids):
        s_artist = get_artist_fn(s_am_id)
        if s_artist:
            models.SongArtist.objects.create(song=song_obj, artist=s_artist, position=j + 1)

def _get_or_create_song(song_in, get_artist_fn) -> Optional[models.Song]:
    if song_in.song_id: return models.Song.objects.filter(pk=song_in.song_id).first()
    song_obj = models.Song.objects.create(
        apple_music_id=song_in.apple_music_id, title=song_in.title,
        length=song_in.length or 0, preview=song_in.preview_url,
        apple_music=song_in.apple_music_url, release_date=song_in.release_date,
        is_out=song_in.is_out,
    )
    if song_in.genres: get_or_create_song_genres(song_in.genres, song_obj)
    if song_in.artists_apple_music_ids:
        _link_artists_to_song(song_obj, song_in.artists_apple_music_ids, get_artist_fn)
    return song_obj

def _handle_project_songs(project, song_inputs, get_artist_fn) -> int:
    total_length = 0
    for song_in in song_inputs:
        song_obj = _get_or_create_song(song_in, get_artist_fn)
        if song_obj:
            models.ProjectSong.objects.create(
                project=project, song=song_obj, position=song_in.position, disc_number=song_in.disc_number
            )
            total_length += song_obj.length
    return total_length

def _apply_project_metadata(project, data, cover_data):
    if data.genres: get_or_create_project_genres(data.genres, project)
    cover_url, p, s = cover_data
    if cover_url:
        models.Cover.objects.create(image=cover_url, content_object=project, position=1, primary_color=p, secondary_color=s, is_confirmed=True)

def _link_project_artists(project, am_ids, get_artist_fn):
    for i, am_id in enumerate(am_ids or []):
        artist = get_artist_fn(am_id)
        if artist:
            models.ProjectArtist.objects.create(project=project, artist=artist, position=i + 1)

def _resolve_or_create_event(data: PerformanceVideoInput) -> Optional[models.Event]:
    if data.event_id: return models.Event.objects.get(pk=data.event_id)
    if not data.event_name: return None
    series = None
    is_one_time = True
    event_type = data.event_type or "OTHER"
    if data.event_series_id:
        series = models.EventSeries.objects.get(pk=data.event_series_id)
        is_one_time, event_type = False, series.series_type
    elif data.event_series_name:
        series = models.EventSeries.objects.create(name=data.event_series_name, series_type=event_type)
        is_one_time = False
    return models.Event.objects.create(
        event_type=event_type, name=data.event_name, date=data.event_date,
        location=data.event_location or "", is_one_time=is_one_time, series=series
    )

def _create_performance_video_record(data, thumb_data, event, artists_data) -> models.PerformanceVideo:
    t_url, t_p, t_s = thumb_data
    pv = models.PerformanceVideo.objects.create(
        youtube_id=data.youtube_id, title=data.title, channel_name=data.channel_name,
        release_date=data.published_at, length=data.length_ms, youtube=data.youtube_url,
        thumbnail=t_url, primary_color=t_p, secondary_color=t_s,
        number_of_songs=len(data.songs_ids or []), event=event
    )
    if data.songs_ids: pv.songs.set(models.Song.objects.filter(pk__in=data.songs_ids))
    if data.artists_apple_music_ids:
        nodes = [_get_or_create_artist_node(aid, artists_data) for aid in data.artists_apple_music_ids]
        pv.artists.set([n for n in nodes if n])
    return pv


# -----------------------------------------------------------------------------
# Input Types
# -----------------------------------------------------------------------------

@strawberry_django.input(models.Artist)
class ArtistCreateInput:
    apple_music_id: str
    name: str
    genres: List[str]
    picture: str
    apple_music_url: str



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

@strawberry_django.input(models.Song)
class SongCreateInput:
    position: int
    disc_number: int
    song_id: Optional[strawberry.ID]
    apple_music_id: Optional[str]
    title: Optional[str]
    length: Optional[int]
    preview_url: Optional[str]
    release_date: Optional[datetime]
    is_out: Optional[bool]
    apple_music_url: Optional[str]
    genres: Optional[List[str]]
    artists_apple_music_ids: Optional[List[str]]


@strawberry_django.input(models.Project)
class ProjectCreateInput:
    apple_music_id: str
    title: str
    is_single: bool
    genres: List[str]
    number_of_songs: int
    release_date: datetime
    cover_url: str
    record_label: str
    alternative_versions: List[str]
    apple_music_url: str
    artists_apple_music_ids: List[str]
    songs: List[SongCreateInput]

@strawberry_django.input(models.Comment)
class CommentCreateInput:
    review_id: strawberry.ID
    text: auto
    replying_to_comment_id: Optional[strawberry.ID] = None

@strawberry.input
class CommentUpdateInput:
    id: strawberry.ID
    text: Optional[str] = strawberry.UNSET


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


@strawberry.input
class ReviewDataInput:
    stars: float
    title: str
    text: Optional[str] = None
    subreviews: Optional[List[SubReviewDataInput]] = None


@strawberry.input
class ReviewUpdateInput:
    id: strawberry.ID
    stars: Optional[float] = strawberry.UNSET
    title: Optional[str] = strawberry.UNSET
    text: Optional[str] = strawberry.UNSET
    is_latest: Optional[bool] = strawberry.UNSET


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


@strawberry.type
class Mutation:
    update_artist: types.Artist = strawberry_django.mutations.update(ArtistUpdateInput)
    delete_artist: types.Artist = strawberry_django.mutations.delete(strawberry.ID)

    update_project: types.Project = strawberry_django.mutations.update(ProjectUpdateInput)
    delete_project: types.Project = strawberry_django.mutations.delete(strawberry.ID)

    update_song: types.Song = strawberry_django.mutations.update(SongUpdateInput)
    delete_song: types.Song = strawberry_django.mutations.delete(strawberry.ID)

    update_event_series: types.EventSeries = strawberry_django.mutations.update(EventSeriesUpdateInput)
    delete_event_series: types.EventSeries = strawberry_django.mutations.delete(strawberry.ID)

    update_event: types.Event = strawberry_django.mutations.update(EventUpdateInput)
    delete_event: types.Event = strawberry_django.mutations.delete(strawberry.ID)

    update_subreview: types.SubReview = strawberry_django.mutations.update(SubReviewUpdateInput)
    delete_subreview: types.SubReview = strawberry_django.mutations.delete(strawberry.ID)

    update_music_video: types.MusicVideo = strawberry_django.mutations.update(MusicVideoUpdateInput)
    delete_music_video: types.MusicVideo = strawberry_django.mutations.delete(strawberry.ID)
    update_performance_video: types.PerformanceVideo = strawberry_django.mutations.update(PerformanceVideoUpdateInput)
    delete_performance_video: types.PerformanceVideo = strawberry_django.mutations.delete(strawberry.ID)

    update_podcast: types.Podcast = strawberry_django.mutations.update(PodcastUpdateInput)
    delete_podcast: types.Podcast = strawberry_django.mutations.delete(strawberry.ID)

    update_outfit: types.Outfit = strawberry_django.mutations.update(OutfitUpdateInput)
    delete_outfit: types.Outfit = strawberry_django.mutations.delete(strawberry.ID)

    update_profile: types.Profile = strawberry_django.mutations.update(ProfileUpdateInput)


    @strawberry.mutation
    async def create_report(
            self,
            info,
            object_id: strawberry.ID,
            model_name: str,
            reason: str
    ) -> types.CreateReportPayload:
        def _sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required")

            # 1. Dynamically find the model type
            try:
                target_ct = ContentType.objects.get(app_label='STARS', model=model_name.lower())
            except ContentType.DoesNotExist:
                raise Exception(f"Invalid model name: {model_name}")

            # 2. Fetch the actual object being reported
            try:
                target_object = target_ct.get_object_for_this_type(pk=object_id)
            except Exception:
                raise Exception(f"Object with ID {object_id} in {model_name} does not exist.")

            # 3. Create the report by assigning the object directly
            models.Report.objects.create(
                user=user,
                reason=reason,
                content_object=target_object  # Django handles content_type and object_id automatically
            )
            return types.CreateReportPayload(created_successfully=True)

        return await database_sync_to_async(_sync)()


    @strawberry.mutation
    async def create_search_history(self, info: strawberry.Info, data: SearchHistoryCreateInput) -> types.SearchHistory:
        def _sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required")

            # Manually create so we can attach the logged-in user
            search_entry = models.SearchHistory.objects.create(
                user=user,
                query=data.query,
                category=data.category.upper()
            )
            return search_entry

        return await database_sync_to_async(_sync)()

    @strawberry.mutation
    async def import_all_top_podcasts(self, info) -> SuccessMessage:
        """
        Massive import: Fetches Top 200 podcasts from every genre ~5000 total.
        """
        user = info.context.request.user
        if not user.is_staff:  # Optional security check
            raise Exception("Unauthorized access.")

        itunes_service = iTunesService()

        # 1. Parallel Fetching
        tasks = []
        for genre_id in ITUNES_GENRES.keys():
            tasks.append(itunes_service.get_podcasts_by_genre(genre_id, limit=200))

        print("Starting massive iTunes fetch...")
        all_results_lists = await asyncio.gather(*tasks)
        await itunes_service.close()

        flat_results = [item for sublist in all_results_lists for item in sublist]

        # 2. Database Save (Sync Wrapper)
        def _bulk_save():
            created_count = 0
            # Deduplicate by ID before hitting DB
            unique_podcasts = {str(p.get("collectionId")): p for p in flat_results}

            with transaction.atomic():
                for collection_id, item in unique_podcasts.items():
                    if not collection_id: continue

                    # Check existence
                    if models.Podcast.objects.filter(apple_podcasts_id=collection_id).exists():
                        continue

                    # Parse Date
                    try:
                        since_date = parser.parse(item.get("releaseDate", "")).date()
                    except:
                        since_date = datetime.now().date()

                    # Create Podcast
                    podcast = models.Podcast.objects.create(
                        apple_podcasts_id=collection_id,
                        title=item.get("collectionName", "Unknown")[:500],
                        host=item.get("artistName", "Unknown")[:500],
                        since=since_date,
                        apple_podcasts=item.get("collectionViewUrl")
                    )

                    get_or_create_podcast_genres(item.get("genres", []), podcast)

                    cover_url = get_high_res_artwork(item.get("artworkUrl600", ""))

                    if cover_url:
                        try:
                            cover_image_url, cover_primary, cover_secondary = process_image_from_url(cover_url)
                        except Exception as e:
                            print(f"Error processing podcast cover image: {e}")

                    if cover_image_url:
                        models.Cover.objects.create(
                            image=cover_image_url,
                            content_object=podcast,
                            position=1,
                            primary_color=cover_primary,
                            secondary_color=cover_secondary
                        )

                    created_count += 1
            return created_count

        count = await database_sync_to_async(_bulk_save)()
        return SuccessMessage(message=f"Imported {count} new podcasts.")

    @strawberry.mutation
    async def import_podcast_from_itunes(self, info, apple_podcasts_id: str) -> types.Podcast:
        """
        Imports a single podcast when a user clicks it in search results.
        """
        # 1. Check Local DB First
        existing = await sync_to_async(models.Podcast.objects.filter(apple_podcasts_id=apple_podcasts_id).first)()
        if existing:
            return existing

        # 2. Fetch from API
        itunes_service = iTunesService()
        item = await itunes_service.lookup_podcast(apple_podcasts_id)
        await itunes_service.close()

        if not item:
            raise Exception("Podcast not found on iTunes.")

        # -------------------------------------------------------
        # 2. ASYNC PHASE: Network Operations (Apple Music + Images)
        # -------------------------------------------------------

        # 3. Save to DB
        def _save_sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                # Double check inside transaction
                if models.Podcast.objects.filter(apple_podcasts_id=apple_podcasts_id).exists():
                    return models.Podcast.objects.get(apple_podcasts_id=apple_podcasts_id)

                try:
                    since_date = parser.parse(item.get("releaseDate", "")).date()
                except:
                    since_date = datetime.now().date()

                podcast = models.Podcast.objects.create(
                    apple_podcasts_id=str(item.get("collectionId")),
                    title=item.get("collectionName", "Unknown")[:500],
                    host=item.get("artistName", "Unknown")[:500],
                    since=since_date,
                    apple_podcasts=item.get("collectionViewUrl")
                )

                get_or_create_podcast_genres(item.get("genres", []), podcast)

                cover_url = get_high_res_artwork(item.get("artworkUrl600", ""))

                if cover_url:
                    try:
                        cover_image_url, cover_primary, cover_secondary = process_image_from_url(cover_url)
                    except Exception as e:
                        print(f"Error processing podcast cover image: {e}")

                if cover_image_url:
                    models.Cover.objects.create(
                        image=cover_image_url,
                        content_object=podcast,
                        position=1,
                        primary_color=cover_primary,
                        secondary_color=cover_secondary,
                        is_confirmed = True
                    )

                return podcast

        return await database_sync_to_async(_save_sync)()


    @strawberry.mutation
    async def add_music_video(self, info, data: MusicVideoInput) -> types.MusicVideo:

        def _sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                uploaded_url, primary_color, secondary_color = process_image_from_url(data.thumbnail_url)

                if not uploaded_url:
                    # Handle the case where image processing failed, or let it fail gracefully
                    # For now, we proceed, but you might want to raise an Exception here
                    pass

                mv = models.MusicVideo.objects.create(
                    youtube_id=data.youtube_id,
                    title=data.title,
                    channel_name=data.channel_name,
                    release_date=data.published_at,
                    length=data.length_ms,
                    youtube=data.youtube_url,
                    thumbnail=uploaded_url,
                    primary_color=primary_color,
                    secondary_color=secondary_color,
                    number_of_songs=len(data.songs_ids)
                )

                songs = list(models.Song.objects.filter(pk__in=data.songs_ids))
                mv.songs.set(songs)

            return mv

        return await database_sync_to_async(_sync)()


    @strawberry.mutation
    async def add_performance_video(self, info: Info, data: PerformanceVideoInput) -> types.PerformanceVideo:
        am_service = AppleMusicService()

        # 1. ID Swap & Global Sanitization
        data.artists_apple_music_ids = _prepare_am_ids(data.artists_apple_music_ids)

        # 2. Async Preparation
        artists_to_create_data = await _fetch_performance_artists(
            set(data.artists_apple_music_ids),
            am_service
        )
        thumb_data = await sync_to_async(process_image_from_url)(data.thumbnail_url)
        await am_service.close()

        # 3. Synchronous Execution
        def _sync():
            if not info.context.request.user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                event = _resolve_or_create_event(data)
                # --- TITLE CONSTRUCTION LOGIC ---
                # 1. Get Artist names (from fetched data or DB)
                artist_names = []
                for am_id in data.artists_apple_music_ids:
                    artist = _get_or_create_artist_node(am_id, artists_to_create_data)
                    if artist:
                        artist_names.append(artist.name)

                # 2. Get Song titles
                song_titles = list(models.Song.objects.filter(
                    pk__in=data.songs_ids
                ).values_list('title', flat=True))

                # 3. Format the strings
                artists_str = _format_list_to_string(artist_names)
                songs_str = _format_list_to_string(song_titles)

                # 4. Assemble: "Artist A & Artist B performing Song X & Song Y"
                new_title = f"{artists_str} performing {songs_str}"

                # 5. Add Event suffix if applicable
                if event:
                    new_title = f"{new_title} ({event.name})"

                data.title = new_title
                # --------------------------------
                return _create_performance_video_record(
                    data, thumb_data, event, artists_to_create_data
                )

        return await database_sync_to_async(_sync)()
    '''
    @strawberry.mutation
    async def create_artist(self, info: Info, data: ArtistCreateInput) -> types.Artist:
        def _create_sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            # ✅ 1. Check if artist already exists
            if data.apple_music_id:
                existing_artist = models.Artist.objects.filter(apple_music_id=data.apple_music_id).first()
                if existing_artist:
                    return existing_artist

            with transaction.atomic():
                # 2. Process Image (Fetch -> Upload -> Get Colors)
                pic_url, primary, secondary = process_image_from_url(data.picture_url)

                # 3. Create Artist
                artist = models.Artist.objects.create(
                    apple_music_id=data.apple_music_id,
                    name=data.name,
                    picture=pic_url or "",  # Fallback if fetch failed
                    primary_color=primary,
                    secondary_color=secondary,
                    apple_music=data.apple_music_url,
                )

                # 4. Handle Genres
                get_or_create_artist_genres(data.genres, artist)

                return artist

        return await database_sync_to_async(_create_sync)()
    '''

    @strawberry.mutation
    async def create_project(self, info: Info, data: ProjectCreateInput) -> types.Project:
        am_service = AppleMusicService()

        # 1. Preparation & ID Swapping
        data.artists_apple_music_ids = _prepare_am_ids(data.artists_apple_music_ids)
        all_am_ids = set(data.artists_apple_music_ids)

        for s in (data.songs or []):
            s.artists_apple_music_ids = _prepare_am_ids(s.artists_apple_music_ids)
            if not s.song_id:
                all_am_ids.update(s.artists_apple_music_ids)

        # 2. Async Network Calls
        cover_data = await _process_cover(data.cover_url)
        artists_to_create_data = await _fetch_missing_artist_data(all_am_ids, am_service)
        await am_service.close()

        # 3. Database Transaction
        def _create_sync():
            if not info.context.request.user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                # Artist Node Creator (closure)
                def get_artist_node(am_id):
                    artist = models.Artist.objects.filter(apple_music_id=am_id).first()
                    if not artist and am_id in artists_to_create_data:
                        artist = _create_artist_from_data(am_id, artists_to_create_data[am_id])
                    return artist

                # Create Project
                project = models.Project.objects.create(
                    apple_music_id=data.apple_music_id, title=data.title,
                    number_of_songs=data.number_of_songs, release_date=data.release_date,
                    project_type=_determine_project_type(data.is_single, data.number_of_songs),
                    apple_music=data.apple_music_url, record_label=data.record_label
                )

                # Metadata & Artists
                _apply_project_metadata(project, data, cover_data)
                _link_project_artists(project, data.artists_apple_music_ids, get_artist_node)

                # Songs
                project.length = _handle_project_songs(project, data.songs or [], get_artist_node)
                project.save(update_fields=["length"])

                if data.alternative_versions:
                    project.alternative_versions.set(models.Project.objects.filter(pk__in=data.alternative_versions))

                return project

        return await database_sync_to_async(_create_sync)()


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
                review = models.Review.objects.select_for_update().get(pk=data.review_id)

                new_comments_count = review.comments_count + 1

                review.comments_count = new_comments_count

                review.save(update_fields=["comments_count"])

                comment_to_reply_to = None
                if data.replying_to_comment_id:
                    try:
                        comment_to_reply_to = models.Comment.objects.select_for_update().get(
                            pk=data.replying_to_comment_id
                        )
                        comment_to_reply_to.number_of_replies += 1
                        comment_to_reply_to.save(update_fields=["number_of_replies"])
                    except models.Comment.DoesNotExist:
                        raise Exception("The comment you are trying to reply to does not exist.")

                comment = models.Comment.objects.create(
                    review=review,
                    user=user,
                    text=data.text,
                    replying_to=comment_to_reply_to,
                )
                return comment

        return await database_sync_to_async(_create_sync)()

    @strawberry.mutation
    async def delete_comment(self, info: Info, comment_id: strawberry.ID) -> types.Comment:
        def _delete_sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                comment = models.Comment.objects.filter(pk=comment_id).first()
                if not comment:
                    raise Exception("Comment not found.")

                if comment.user != user:
                    raise Exception("You can only delete your own comments.")

                review = models.Review.objects.select_for_update().get(pk=comment.review_id)

                comment.delete()

                if review:
                    new_comments_count = review.comments_count - 1
                    review.comments_count = new_comments_count
                    review.save(update_fields=["comments_count"])

                return comment

        return await database_sync_to_async(_delete_sync)()


    @strawberry.mutation
    async def like_dislike_comment(
            self, info: Info, comment_id: strawberry.ID, action: LikeAction
    ) -> types.Comment:
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
                    if comment.liked_by.filter(pk=user.pk).exists():
                        # already liked → unlike
                        comment.liked_by.remove(user)
                        comment.likes_count -= 1
                    else:
                        # not liked → like, and remove dislike if present
                        comment.liked_by.add(user)
                        comment.likes_count += 1
                        if comment.disliked_by.filter(pk=user.pk).exists():
                            comment.disliked_by.remove(user)
                            comment.dislikes_count -= 1

                elif action == LikeAction.DISLIKE:
                    if comment.disliked_by.filter(pk=user.pk).exists():
                        # already disliked → undislike
                        comment.disliked_by.remove(user)
                        comment.dislikes_count -= 1
                    else:
                        # not disliked → dislike, and remove like if present
                        comment.disliked_by.add(user)
                        comment.dislikes_count += 1
                        if comment.liked_by.filter(pk=user.pk).exists():
                            comment.liked_by.remove(user)
                            comment.likes_count -= 1

                comment.save(update_fields=["likes_count", "dislikes_count"])
                return comment

        return await database_sync_to_async(_update_sync)()

    @strawberry.mutation
    async def like_dislike_review(
            self, info: Info, review_id: strawberry.ID, action: LikeAction
    ) -> types.Review:
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
                    if review.liked_by.filter(pk=user.pk).exists():
                        # already liked → unlike
                        review.liked_by.remove(user)
                        review.likes_count -= 1
                    else:
                        # not liked → like, and remove dislike if present
                        review.liked_by.add(user)
                        review.likes_count += 1
                        if review.disliked_by.filter(pk=user.pk).exists():
                            review.disliked_by.remove(user)
                            review.dislikes_count -= 1

                elif action == LikeAction.DISLIKE:
                    if review.disliked_by.filter(pk=user.pk).exists():
                        # already disliked → undislike
                        review.disliked_by.remove(user)
                        review.dislikes_count -= 1
                    else:
                        # not disliked → dislike, and remove like if present
                        review.disliked_by.add(user)
                        review.dislikes_count += 1
                        if review.liked_by.filter(pk=user.pk).exists():
                            review.liked_by.remove(user)
                            review.likes_count -= 1

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

                old_latest = (
                    models.Review.objects
                    .select_for_update()
                    .filter(
                        user=user,
                        object_id=project.id,
                        content_type__model='project',
                        is_latest=True
                    )
                    .first()
                )

                old_reviews_count = project.reviews_count
                old_star_total = project.star_average * old_reviews_count

                if old_latest:
                    old_latest.is_latest = False
                    old_latest.save(update_fields=['is_latest'])

                    old_reviews_count -= 1
                    old_star_total -= float(old_latest.stars)

                review = models.Review.objects.create(
                    user=user,
                    title=data.title,
                    stars=data.stars,
                    text=data.text,
                    content_object=project
                )

                if data.subreviews:
                    for i, sub in enumerate(data.subreviews, start=1):
                        models.SubReview.objects.create(
                            review=review,
                            topic=sub.topic,
                            text=sub.text or "",
                            stars=sub.stars,
                            position=i
                        )

                new_reviews_count = old_reviews_count + 1
                new_star_total = old_star_total + float(data.stars)
                new_average = new_star_total / new_reviews_count if new_reviews_count > 0 else 0.0

                if new_average < 0.0:
                    new_average = 0.0

                if new_average > 5.0:
                    new_average = 5.0

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

                old_latest = (
                    models.Review.objects
                    .select_for_update()
                    .filter(
                        user=user,
                        object_id=song.id,
                        content_type__model='song',
                        is_latest=True
                    )
                    .first()
                )

                old_reviews_count = song.reviews_count
                old_star_total = song.star_average * old_reviews_count

                if old_latest:
                    old_latest.is_latest = False
                    old_latest.save(update_fields=['is_latest'])

                    old_reviews_count -= 1
                    old_star_total -= float(old_latest.stars)

                review = models.Review.objects.create(
                    user=user,
                    title=data.title,
                    stars=data.stars,
                    text=data.text,
                    content_object=song
                )

                if data.subreviews:
                    for i, sub in enumerate(data.subreviews, start=1):
                        models.SubReview.objects.create(
                            review=review,
                            topic=sub.topic,
                            text=sub.text or "",
                            stars=sub.stars,
                            position=i
                        )

                new_reviews_count = old_reviews_count + 1
                new_star_total = old_star_total + float(data.stars)
                new_average = new_star_total / new_reviews_count if new_reviews_count > 0 else 0.0

                if new_average < 0.0:
                    new_average = 0.0

                if new_average > 5.0:
                    new_average = 5.0

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

                old_latest = (
                    models.Review.objects
                    .select_for_update()
                    .filter(
                        user=user,
                        object_id=outfit.id,
                        content_type__model='outfit',
                        is_latest=True
                    )
                    .first()
                )

                old_reviews_count = outfit.reviews_count
                old_star_total = outfit.star_average * old_reviews_count

                if old_latest:
                    old_latest.is_latest = False
                    old_latest.save(update_fields=['is_latest'])

                    old_reviews_count -= 1
                    old_star_total -= float(old_latest.stars)

                review = models.Review.objects.create(
                    user=user,
                    title=data.title,
                    stars=data.stars,
                    text=data.text,
                    content_object=outfit
                )

                if data.subreviews:
                    for i, sub in enumerate(data.subreviews, start=1):
                        models.SubReview.objects.create(
                            review=review,
                            topic=sub.topic,
                            text=sub.text or "",
                            stars=sub.stars,
                            position=i
                        )

                new_reviews_count = old_reviews_count + 1
                new_star_total = old_star_total + float(data.stars)
                new_average = new_star_total / new_reviews_count if new_reviews_count > 0 else 0.0

                if new_average < 0.0:
                    new_average = 0.0

                if new_average > 5.0:
                    new_average = 5.0

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

                old_latest = (
                    models.Review.objects
                    .select_for_update()
                    .filter(
                        user=user,
                        object_id=podcast.id,
                        content_type__model='podcast',
                        is_latest=True
                    )
                    .first()
                )

                old_reviews_count = podcast.reviews_count
                old_star_total = podcast.star_average * old_reviews_count

                if old_latest:
                    old_latest.is_latest = False
                    old_latest.save(update_fields=['is_latest'])

                    old_reviews_count -= 1
                    old_star_total -= float(old_latest.stars)

                review = models.Review.objects.create(
                    user=user,
                    title=data.title,
                    stars=data.stars,
                    text=data.text,
                    content_object=podcast
                )

                if data.subreviews:
                    for i, sub in enumerate(data.subreviews, start=1):
                        models.SubReview.objects.create(
                            review=review,
                            topic=sub.topic,
                            text=sub.text or "",
                            stars=sub.stars,
                            position=i
                        )

                new_reviews_count = old_reviews_count + 1
                new_star_total = old_star_total + float(data.stars)
                new_average = new_star_total / new_reviews_count if new_reviews_count > 0 else 0.0

                if new_average < 0.0:
                    new_average = 0.0

                if new_average > 5.0:
                    new_average = 5.0

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

                old_latest = (
                    models.Review.objects
                    .select_for_update()
                    .filter(
                        user=user,
                        object_id=music_video.id,
                        content_type__model='music_video',
                        is_latest=True
                    )
                    .first()
                )

                old_reviews_count = music_video.reviews_count
                old_star_total = music_video.star_average * old_reviews_count

                if old_latest:
                    old_latest.is_latest = False
                    old_latest.save(update_fields=['is_latest'])

                    old_reviews_count -= 1
                    old_star_total -= float(old_latest.stars)

                review = models.Review.objects.create(
                    user=user,
                    title=data.title,
                    stars=data.stars,
                    text=data.text,
                    content_object=music_video
                )

                if data.subreviews:
                    for i, sub in enumerate(data.subreviews, start=1):
                        models.SubReview.objects.create(
                            review=review,
                            topic=sub.topic,
                            text=sub.text or "",
                            stars=sub.stars,
                            position=i
                        )

                new_reviews_count = old_reviews_count + 1
                new_star_total = old_star_total + float(data.stars)
                new_average = new_star_total / new_reviews_count if new_reviews_count > 0 else 0.0

                if new_average < 0.0:
                    new_average = 0.0

                if new_average > 5.0:
                    new_average = 5.0

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

                old_latest = (
                    models.Review.objects
                    .select_for_update()
                    .filter(
                        user=user,
                        title=data.title,
                        object_id=cover.id,
                        content_type__model='cover',
                        is_latest=True
                    )
                    .first()
                )

                old_reviews_count = cover.reviews_count
                old_star_total = cover.star_average * old_reviews_count

                if old_latest:
                    old_latest.is_latest = False
                    old_latest.save(update_fields=['is_latest'])

                    old_reviews_count -= 1
                    old_star_total -= float(old_latest.stars)

                review = models.Review.objects.create(
                    user=user,
                    stars=data.stars,
                    text=data.text,
                    content_object=cover
                )

                if data.subreviews:
                    for i, sub in enumerate(data.subreviews, start=1):
                        models.SubReview.objects.create(
                            review=review,
                            topic=sub.topic,
                            text=sub.text or "",
                            stars=sub.stars,
                            position=i
                        )

                new_reviews_count = old_reviews_count + 1
                new_star_total = old_star_total + float(data.stars)
                new_average = new_star_total / new_reviews_count if new_reviews_count > 0 else 0.0

                if new_average < 0.0:
                    new_average = 0.0

                if new_average > 5.0:
                    new_average = 5.0

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
                review = models.Review.objects.select_for_update().get(pk=review_id)

                current_count = review.subreviews.count()
                new_position = current_count + 1

                sub_review = models.SubReview.objects.create(
                    review=review,
                    topic=data.topic,
                    text=data.text,
                    stars=data.stars,
                    position = new_position
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

                stars_to_remove = float(review.stars)

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

                if isinstance(review_object, models.Project):
                    obj = review_object
                elif isinstance(review_object, models.Song):
                    obj = review_object
                elif isinstance(review_object, models.Cover):
                    obj = review_object
                elif isinstance(review_object, models.MusicVideo):
                    obj = review_object
                elif isinstance(review_object, models.Podcast):
                    obj = review_object
                elif isinstance(review_object, models.Outfit):
                    obj = review_object
                elif isinstance(review_object, models.Event):
                    obj = review_object
                else:
                    obj = None

                if obj:
                    if latest_review:
                        # replace stars (subtract old, add new)
                        old_total = obj.star_average * obj.reviews_count
                        new_total = old_total - stars_to_remove + float(latest_review.stars)
                        obj.star_average = new_total / obj.reviews_count if obj.reviews_count > 0 else 0.0
                    else:
                        # no latest → user has no more reviews on this object
                        obj.reviews_count = obj.reviews_count - 1 if obj.reviews_count > 0 else 0
                        if obj.reviews_count == 0:
                            obj.star_average = 0.0
                        else:
                            new_total = obj.star_average * (obj.reviews_count + 1) - stars_to_remove
                            obj.star_average = new_total / obj.reviews_count

                    obj.save(update_fields=['reviews_count', 'star_average'])

                return review

        return await database_sync_to_async(_delete_sync)()

    @strawberry.mutation
    async def edit_review(self, info: Info, data: ReviewUpdateInput) -> types.Review:
        def _edit_sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                review = models.Review.objects.select_for_update().filter(pk=data.id).first()
                if not review:
                    raise Exception("Review not found.")

                if review.user != user:
                    raise Exception("You can only edit your own reviews.")

                review_object = review.content_object
                old_stars = float(review.stars)

                # Track if we need to update star average
                update_star_average = False
                if data.stars is not strawberry.UNSET and review.is_latest and old_stars != float(data.stars):
                    update_star_average = True

                # Update review fields
                if data.stars is not strawberry.UNSET:
                    review.stars = float(data.stars)
                if data.text is not strawberry.UNSET:
                    review.text = data.text
                if data.title is not strawberry.UNSET:
                    review.title = data.title
                if data.is_latest is not strawberry.UNSET:
                    review.is_latest = data.is_latest

                review.save(update_fields=['stars', 'text', 'title', 'is_latest'])

                # Only update object star_average if necessary
                if update_star_average:
                    if isinstance(review_object, models.Project):
                        obj = review_object
                    elif isinstance(review_object, models.Song):
                        obj = review_object
                    elif isinstance(review_object, models.Cover):
                        obj = review_object
                    elif isinstance(review_object, models.MusicVideo):
                        obj = review_object
                    elif isinstance(review_object, models.Podcast):
                        obj = review_object
                    elif isinstance(review_object, models.Outfit):
                        obj = review_object
                    elif isinstance(review_object, models.Event):
                        obj = review_object
                    else:
                        obj = None

                    if obj:
                        # adjust star_average
                        total_stars = obj.star_average * obj.reviews_count
                        total_stars = total_stars - old_stars + float(review.stars)
                        obj.star_average = total_stars / obj.reviews_count if obj.reviews_count > 0 else 0
                        obj.save(update_fields=['star_average'])

                return review

        return await database_sync_to_async(_edit_sync)()


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

                conversation.seen_by.clear()
                conversation.seen_by.add(user)

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

                transaction.on_commit(lambda: async_to_sync(broadcast_message_event)(message.id, message.conversation_id, "created"))
                transaction.on_commit(lambda: async_to_sync(broadcast_conversation_update)(conversation.id))

                return message

        return await database_sync_to_async(_add_message_sync)()

    @strawberry.mutation
    async def mark_conversation_as_seen_by_user(self, info: Info, conversation_id: strawberry.ID) -> SuccessMessage:
        request = info.context.request

        def _mark_seen_sync():
            user = request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                try:
                    conversation = models.Conversation.objects.get(pk=conversation_id)
                except models.Conversation.DoesNotExist:
                    raise Exception("Conversation not found.")

                is_participant = conversation.participants.filter(id=user.id).exists()
                if not is_participant:
                    raise Exception("You are not a participant in this conversation.")

                conversation.seen_by.add(user)

            return SuccessMessage(message="Conversation marked as seen.")

        return await database_sync_to_async(_mark_seen_sync)()

    @strawberry.mutation
    async def delete_message(self, info: Info, id: strawberry.ID) -> SuccessMessage:
        def _delete_message_sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                try:
                    message = models.Message.objects.select_related('conversation').get(pk=id)
                except (models.Message.DoesNotExist, ValueError):
                    raise Exception("Message not found.")

                if message.sender != user:
                    raise Exception("You can only delete your own messages.")

                rememeber_message_id = message.id
                remmeber_conversation_id = message.conversation_id

                message.delete()

                transaction.on_commit(
                    lambda: async_to_sync(broadcast_message_event)(rememeber_message_id, remmeber_conversation_id, "deleted")
                )

                return SuccessMessage(message="Message deleted successfully.")

        return await database_sync_to_async(_delete_message_sync)()

    @strawberry.mutation
    async def like_message(self, info: Info, id: strawberry.ID) -> SuccessMessage:
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

                transaction.on_commit(lambda: async_to_sync(broadcast_message_event)(message.id, message.conversation_id, "updated"))

                return SuccessMessage(message="Message liked successfully.")

        return await database_sync_to_async(_like_message_sync)()

    @strawberry.mutation
    async def mark_messages_as_read(self, info, conversation_id: strawberry.ID) -> SuccessMessage:
        """Mark all messages from other users in the conversation as read"""

        def _sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                # Fetch unread messages first
                unread_messages = list(
                    models.Message.objects
                    .filter(conversation_id=conversation_id)
                    .exclude(sender=user)
                    .filter(is_read=False)
                )

                # Bulk update in DB
                models.Message.objects.filter(id__in=[m.id for m in unread_messages]).update(is_read=True)

                # Broadcast individually after commit
                for m in unread_messages:
                    m.is_read = True  # update instance in memory
                    transaction.on_commit(lambda m=m: async_to_sync(broadcast_message_event)(m.id, m.conversation_id, "updated"))

            return SuccessMessage(message=f"Marked {len(unread_messages)} messages as read.")

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

                transaction.on_commit(lambda: async_to_sync(broadcast_message_event)(message.id, message.conversation_id, "updated"))

            return SuccessMessage(message="Message marked as delivered.")

        return await database_sync_to_async(_sync)()

    @strawberry.mutation
    async def add_cover_to_project(self, info, project_id: strawberry.ID, data: CoverDataInput) -> types.Cover:

        def _sync():
            user = info.context.request.user
            if not user.is_authenticated:
                raise Exception("Authentication required.")

            with transaction.atomic():
                is_confirmed = False

                if user.is_staff or user.is_superuser:
                    is_confirmed = True

                project = models.Project.objects.get(pk=project_id)

                # Determine position
                existing_count = models.Cover.objects.filter(
                    content_type=ContentType.objects.get_for_model(project),
                    object_id=project.id
                ).count()
                position = existing_count + 1

                # 1. Decode and save base64 image to temp file
                image_data = base64.b64decode(data.image_file)
                # Using suffix .png as in your original snippet
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                    temp_file.write(image_data)
                    temp_file.flush()
                    temp_path = temp_file.name

                try:
                    # 2. Upload to Cloudinary and request colors
                    upload_result = cloudinary.uploader.upload(
                        temp_path,
                        colors=True,
                    )

                    uploaded_url = upload_result.get("secure_url")
                    raw_colors = upload_result.get("colors", [])

                    # 3. Extract raw hex colors
                    raw_primary = raw_colors[0][0] if len(raw_colors) > 0 else None
                    raw_secondary = raw_colors[1][0] if len(raw_colors) > 1 else None

                    # 4. Apply the "Magic" Muting logic
                    # Using 0.55 as per your helper function's suggestion
                    primary_muted = ensure_muted_color(raw_primary, max_saturation=0.55)
                    secondary_muted = ensure_muted_color(raw_secondary, max_saturation=0.55)

                    # 5. Create Cover with processed colors
                    cover = models.Cover.objects.create(
                        image=uploaded_url,
                        content_object=project,
                        position=position,
                        primary_color=primary_muted,
                        secondary_color=secondary_muted,
                        is_confirmed=is_confirmed,
                        user=user,
                    )
                    return cover

                finally:
                    # Clean up the temporary file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)

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