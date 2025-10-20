import strawberry
import strawberry_django
from strawberry_django.optimizer import DjangoOptimizerExtension
from strawberry_django.relay import DjangoCursorConnection
from typing import List, Dict

from . import types, filters, mutations, subscriptions, orders
from django.db.models import OuterRef, Subquery, Exists
from STARS import models
from STARS.services.apple_music import AppleMusicService

apple_music = AppleMusicService()

# --- GraphQL types ---
@strawberry.type
class AppleMusicArtistLight:
    id: str
    name: str

@strawberry.type
class AppleMusicAlbumLight:
    id: str
    name: str
    release_date: str
    cover_url: str
    artists: List[AppleMusicArtistLight]

@strawberry.type
class AppleMusicSongDetail:
    id: str
    name: str
    length_ms: int
    preview_url: str
    artists: List[AppleMusicArtistLight]

@strawberry.type
class AppleMusicAlbumDetail:
    id: str
    name: str
    release_date: str
    cover_url: str
    songs: List[AppleMusicSongDetail]
    artists: List[AppleMusicArtistLight]

# --- GraphQL Query ---
@strawberry.type
class Query:
    # --- Lightweight query: all albums of an artist ---
    @strawberry.field
    async def get_artist_albums(self, artist_id: str) -> List[AppleMusicAlbumLight]:
        results = await apple_music.get_albums_by_artist(artist_id)
        albums = []

        for album in results:
            album_attrs = album.get("attributes", {})
            artwork = album_attrs.get("artwork", {})
            cover_url = artwork.get("url", "") if artwork else ""

            # Proper artist fetching via relationships
            artists: List[AppleMusicArtistLight] = []
            for artist_data in album.get("relationships", {}).get("artists", {}).get("data", []):
                artists.append(
                    AppleMusicArtistLight(
                        id=artist_data.get("id", ""),
                        name=album_attrs.get("artistName", "")
                    )
                )

            albums.append(
                AppleMusicAlbumLight(
                    id=album.get("id"),
                    name=album_attrs.get("name", ""),
                    release_date=album_attrs.get("releaseDate", ""),
                    cover_url=cover_url,
                    artists=artists
                )
            )
        return albums

    # --- Detailed query: one album with songs and preview URLs ---
    @strawberry.field
    async def get_album_detail(self, album_id: str) -> AppleMusicAlbumDetail:
        album = await apple_music.get_album_by_id(album_id)
        album_attrs = album.get("attributes", {})
        artwork = album_attrs.get("artwork", {})
        cover_url = artwork.get("url", "") if artwork else ""

        # Artists
        artists: List[AppleMusicArtistLight] = []
        for artist_data in album.get("relationships", {}).get("artists", {}).get("data", []):
            artists.append(
                AppleMusicArtistLight(
                    id=artist_data.get("id", ""),
                    name=album_attrs.get("artistName", "")
                )
            )

        # Songs
        songs: List[AppleMusicSongDetail] = []
        tracks_data = album.get("relationships", {}).get("tracks", {}).get("data", [])
        for track in tracks_data:
            track_attrs = track.get("attributes", {})
            track_artists: List[AppleMusicArtistLight] = []
            for artist_data in track.get("relationships", {}).get("artists", {}).get("data", []):
                track_artists.append(
                    AppleMusicArtistLight(
                        id=artist_data.get("id", ""),
                        name=artist_data.get("name", "")
                    )
                )

            songs.append(
                AppleMusicSongDetail(
                    id=track.get("id"),
                    name=track_attrs.get("name", ""),
                    length_ms=track_attrs.get("durationInMillis", 0),
                    preview_url=track_attrs.get("previews", [{}])[0].get("url", ""),
                    artists=track_artists
                )
            )

        return AppleMusicAlbumDetail(
            id=album.get("id"),
            name=album_attrs.get("name", ""),
            release_date=album_attrs.get("releaseDate", ""),
            cover_url=cover_url,
            songs=songs,
            artists=artists
        )

    artists: DjangoCursorConnection[types.Artist] = strawberry_django.connection(filters=filters.ArtistFilter, order=orders.ArtistOrder)
    projects: DjangoCursorConnection[types.Project] = strawberry_django.connection(filters=filters.ProjectFilter, order=orders.ProjectOrder)
    songs: DjangoCursorConnection[types.Song] = strawberry_django.connection(filters=filters.SongFilter, order=orders.SongOrder)
    podcasts: DjangoCursorConnection[types.Podcast] = strawberry_django.connection(filters=filters.PodcastFilter, order=orders.PodcastOrder)
    outfits: DjangoCursorConnection[types.Outfit] = strawberry_django.connection(filters=filters.OutfitFilter, order=orders.OutfitOrder)
    comments: DjangoCursorConnection[types.Comment] = strawberry_django.connection(filters=filters.CommentFilter, order=orders.CommentOrder)
    reviews: DjangoCursorConnection[types.Review] = strawberry_django.connection(filters=filters.ReviewFilter, order=orders.ReviewOrder)

    def resolve_reviews(self, info, **kwargs):
        current_user = info.context.get("user")
        if not current_user or not current_user.is_authenticated:
            return models.Review.objects.none()

        followed_subquery = models.Profile.objects.filter(
            user=OuterRef('user_id'),  # Review.user_id points to the User
            followers=current_user
        )

        return models.Review.objects.annotate(
            user_followed_by_current_user=Exists(followed_subquery)
        )

    messages: DjangoCursorConnection[types.Message] = strawberry_django.connection(filters=filters.MessageFilter, order=orders.MessageOrder)
    conversations: DjangoCursorConnection[types.Conversation] = strawberry_django.connection(filters=filters.ConversationFilter, order=orders.ConversationOrder)
    events: DjangoCursorConnection[types.Event] = strawberry_django.connection(filters=filters.EventFilter, order=orders.EventOrder)
    event_series: DjangoCursorConnection[types.EventSeries] = strawberry_django.connection(filters=filters.EventSeriesFilter, order=orders.EventSeriesOrder)
    music_videos: DjangoCursorConnection[types.MusicVideo] = strawberry_django.connection(filters=filters.MusicVideoFilter, order=orders.MusicVideoOrder)
    users: DjangoCursorConnection[types.User] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)

    def resolve_users(self, info, **kwargs):
        current_user = info.context["user"]
        if not current_user or not current_user.is_authenticated:
            return models.User.objects.none()

        followed_subquery = models.Profile.objects.filter(
            user=OuterRef('pk'),
            followers=current_user
        )
        return models.User.objects.annotate(
            followed_by_current_user=Exists(followed_subquery)
        )

    # These are not paginated
    project_songs: DjangoCursorConnection[types.ProjectSong] = strawberry_django.connection(filters=filters.ProjectSongFilter, order=orders.ProjectSongOrder)
    project_artists: DjangoCursorConnection[types.ProjectArtist] = strawberry_django.connection(filters=filters.ProjectArtistFilter, order=orders.ProjectArtistOrder)
    song_artists: DjangoCursorConnection[types.SongArtist] = strawberry_django.connection(filters=filters.SongArtistFilter, order=orders.SongArtistOrder)
    sub_reviews: DjangoCursorConnection[types.SubReview] = strawberry_django.connection(filters=filters.SubReviewFilter, order=orders.SubReviewOrder)
    profiles: DjangoCursorConnection[types.Profile] = strawberry_django.connection(filters=filters.ProfileFilter, order=orders.ProfileOrder)
    covers: DjangoCursorConnection[types.Cover] = strawberry_django.connection(filters=filters.CoverFilter, order=orders.CoverOrder)

schema = strawberry.Schema(
    query=Query,
    mutation=mutations.Mutation,
    subscription=subscriptions.Subscription,
    extensions=[DjangoOptimizerExtension],
)