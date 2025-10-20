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

# --- GraphQL types for Apple Music ---
@strawberry.type
class AppleMusicArtist:
    id: str
    name: str
    picture: str = ""  # optional URL

@strawberry.type
class AppleMusicSong:
    id: str
    name: str
    release_date: str = ""
    length_ms: int = 0
    artists: List[AppleMusicArtist]

@strawberry.type
class AppleMusicAlbumCover:
    url: str

@strawberry.type
class AppleMusicAlbum:
    id: str
    name: str
    release_date: str = ""
    length_ms: int = 0
    artists: List[AppleMusicArtist]
    songs: List[AppleMusicSong]
    cover: AppleMusicAlbumCover

# --- Resolver ---
@strawberry.type
class Query:
    @strawberry.field
    async def search_apple_music_albums(self, term: str) -> List[AppleMusicAlbum]:
        results = await apple_music.search_albums(term)
        albums: List[AppleMusicAlbum] = []

        for album in results:
            album_attrs = album.get("attributes", {})

            # Album artists
            album_artists: List[AppleMusicArtist] = []
            for artist_name in album_attrs.get("artistName", "").split(","):
                album_artists.append(
                    AppleMusicArtist(
                        id=artist_name,  # placeholder, real ID requires additional API call
                        name=artist_name,
                        picture=""  # placeholder, you could fetch artist picture later
                    )
                )

            # Songs (empty for now; proper fetching requires a per-album API call)
            songs: List[AppleMusicSong] = []

            # Album cover
            artwork = album_attrs.get("artwork", {})
            cover_url = artwork.get("url", "") if artwork else ""

            albums.append(
                AppleMusicAlbum(
                    id=album.get("id"),
                    name=album_attrs.get("name", ""),
                    release_date=album_attrs.get("releaseDate", ""),
                    length_ms=album_attrs.get("trackCount", 0) * 0,  # placeholder; Apple Music API doesn't provide album length directly
                    artists=album_artists,
                    songs=songs,
                    cover=AppleMusicAlbumCover(url=cover_url)
                )
            )
        return albums

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