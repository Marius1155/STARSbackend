import strawberry
import strawberry_django
from strawberry_django.optimizer import DjangoOptimizerExtension
from strawberry_django.relay import DjangoCursorConnection
from typing import List, Dict, Optional

from django.contrib.postgres.search import TrigramSimilarity, TrigramWordSimilarity
from . import types, filters, mutations, subscriptions, orders
from django.db.models import OuterRef, Subquery, Exists, Q, Value, F
from django.db.models.functions import Concat, Greatest
from STARS import models
from STARS.services.apple_music import AppleMusicService
from STARS.services.youtube import YoutubeService
from asgiref.sync import sync_to_async
from django.core.cache import cache
from STARS.utils.cache import make_cache_key
from strawberry import relay
from datetime import datetime

from STARS.services.itunes import iTunesService

import re

from STARS.utils.cache import cache_graphql_query, CacheKeys
from .orders import SearchHistoryOrder


def get_high_res_artwork(url: str) -> str:
    if not url:
        return ""
    # Regex to find the dimensions part (e.g., "600x600bb") and replace it
    return re.sub(r"\d+x\d+bb", "900x900bb", url)

itunes_service = iTunesService()
apple_music = AppleMusicService()
youtube_service = YoutubeService()

# --- GraphQL types ---
@strawberry.type
class AppleMusicArtistLight:
    id: str
    name: str
    image_url: str

@strawberry.type
class AppleMusicArtistDetail:
    id: str
    name: str
    image_url: str
    url: str
    genre_names: List[str]

@strawberry.type
class AppleMusicSongLight:
    id: str
    name: str
    length_ms: int
    release_date: str
    preview_url: str
    artists_names: str

@strawberry.type
class AppleMusicAlbumLight:
    id: str
    name: str
    release_date: str
    cover_url: str
    primary_color: str
    secondary_color: str
    artists_names: str
    track_count: int
    kind: str
    is_single: bool
    is_complete: bool

@strawberry.type
class AppleMusicSongDetail:
    id: str
    type: str
    name: str
    disc_number: int
    length_ms: int
    preview_url: str
    track_number: int
    release_date: str
    url: str
    genre_names: List[str]
    artists: List[AppleMusicArtistDetail]
    is_out: bool

@strawberry.type
class AppleMusicAlbumDetail:
    id: str
    name: str
    release_date: str
    cover_url: str
    primary_color: str
    secondary_color: str
    track_count: int
    kind: str
    url: str
    is_single: bool
    is_compilation: bool
    is_complete: bool
    genre_names: List[str]
    record_label: str
    songs: List[AppleMusicSongDetail]
    artists: List[AppleMusicArtistDetail]

@strawberry.type
class YoutubeVideoLight:
    id: str
    title: str
    thumbnail_url: str
    channel_name: str
    published_at: str
    url: str

@strawberry.type
class YoutubeVideoDetail:
    id: str
    title: str
    thumbnail_url: str
    channel_name: str
    published_at: str
    length_ms: int
    view_count: str
    url: str
    primary_color: str

@strawberry.type
class iTunesPodcastLight:
    id: str
    title: str
    host: str
    image_url: str


@strawberry.type
class Query:
    @strawberry.field
    async def me(self, info: strawberry.Info) -> Optional[types.User]:
        def get_authenticated_user():
            user = info.context.request.user
            if user and user.is_authenticated:
                return user
            return None

        return await sync_to_async(get_authenticated_user)()

    @strawberry.field
    async def get_popular_projects_by_genre(
            self,
            genre_id: strawberry.ID,
            limit: int = 20
    ) -> List[types.Project]:
        """
        Fetches the most popular projects for a specific MusicGenre.
        Caches IDs only, then hydrates.
        """
        cache_key_val = f"popular_projects_genre_{genre_id}_limit_{limit}"

        @cache_graphql_query(
            CacheKeys.POPULAR_PROJECTS_BY_GENRE,
            timeout=86400,
            key_params=["cache_key_val"]
        )
        async def get_cached_ids(cache_key_val: str) -> List[int]:
            def fetch_ids():
                # 1. Query IDs sorted by the existing popularity_score field
                return list(models.Project.objects.filter(
                    project_genres_ordered__genre_id=genre_id
                ).order_by('-popularity_score').values_list('pk', flat=True)[:limit])

            return await sync_to_async(fetch_ids)()

        # 1. Get ordered IDs from Cache
        ordered_ids = await get_cached_ids(cache_key_val=cache_key_val)

        if not ordered_ids:
            return []

        # 2. Hydrate (Fetch actual objects)
        def fetch_objects():
            # in_bulk fetches objects by ID efficiently
            projects_dict = models.Project.objects.in_bulk(ordered_ids)
            # Reconstruct list in the correct cached order
            return [projects_dict[pk] for pk in ordered_ids if pk in projects_dict]

        return await sync_to_async(fetch_objects)()

    @strawberry.field
    async def get_popular_podcasts_by_genre(
            self,
            genre_id: strawberry.ID,
            limit: int = 20
    ) -> List[types.Podcast]:
        """
        Fetches the most popular podcasts for a specific PodcastGenre.
        Caches IDs only, then hydrates.
        """
        cache_key_val = f"popular_podcasts_genre_{genre_id}_limit_{limit}"

        @cache_graphql_query(
            CacheKeys.POPULAR_PODCASTS_BY_GENRE,
            timeout=86400,
            key_params=["cache_key_val"]
        )
        async def get_cached_ids(cache_key_val: str) -> List[int]:
            def fetch_ids():
                # 1. Query IDs sorted by the existing popularity_score field
                return list(models.Podcast.objects.filter(
                    podcast_genres_ordered__genre_id=genre_id
                ).order_by('-popularity_score').values_list('pk', flat=True)[:limit])

            return await sync_to_async(fetch_ids)()

        # 1. Get ordered IDs from Cache
        ordered_ids = await get_cached_ids(cache_key_val=cache_key_val)

        if not ordered_ids:
            return []

        # 2. Hydrate (Fetch actual objects)
        def fetch_objects():
            podcasts_dict = models.Podcast.objects.in_bulk(ordered_ids)
            return [podcasts_dict[pk] for pk in ordered_ids if pk in podcasts_dict]

        return await sync_to_async(fetch_objects)()

    @strawberry.field
    async def get_music_videos_for_songs(
            self,
            song_ids: List[strawberry.ID]
    ) -> List[types.MusicVideo]:
        """
        Fetches music videos for a list of songs.
        Preserves input song order. Deduplicates.
        """
        if not song_ids:
            return []

        ids_hash = ",".join(str(x) for x in song_ids)

        @cache_graphql_query(
            CacheKeys.MUSIC_VIDEOS_FROM_SONGS,
            timeout=86400,  # ✅ Cached for 24 Hours
            key_params=["ids_hash"]
        )
        async def get_cached_ids(ids_hash: str):
            def fetch():
                # 1. Fetch relations
                relations = models.MusicVideo.objects.filter(
                    songs__id__in=song_ids
                ).values_list('id', 'songs__id')

                # 2. Sort by song order logic
                song_rank = {s_id: i for i, s_id in enumerate(song_ids)}
                valid_relations = [r for r in relations if str(r[1]) in song_rank]
                valid_relations.sort(key=lambda x: song_rank[str(x[1])])

                # 3. Deduplicate (keep first occurrence)
                seen_videos = set()
                ordered_video_ids = []

                for video_id, _ in valid_relations:
                    if video_id not in seen_videos:
                        seen_videos.add(video_id)
                        ordered_video_ids.append(video_id)

                return ordered_video_ids

            return await sync_to_async(fetch)()

        ordered_ids = await get_cached_ids(ids_hash=ids_hash)

        def hydrate_results():
            objs = list(models.MusicVideo.objects.filter(id__in=ordered_ids))
            objs.sort(key=lambda x: ordered_ids.index(x.id))
            return objs

        return await sync_to_async(hydrate_results)()

    @strawberry.field
    async def get_performance_videos_for_songs(
            self,
            song_ids: List[strawberry.ID]
    ) -> List[types.PerformanceVideo]:
        """
        Fetches performance videos for a list of songs.
        Preserves input song order. Deduplicates.
        """
        if not song_ids:
            return []

        ids_hash = ",".join(str(x) for x in song_ids)

        @cache_graphql_query(
            CacheKeys.PERFORMANCE_VIDEOS_FROM_SONGS,
            timeout=86400,  # ✅ Cached for 24 Hours
            key_params=["ids_hash"]
        )
        async def get_cached_ids(ids_hash: str):
            def fetch():
                relations = models.PerformanceVideo.objects.filter(
                    songs__id__in=song_ids
                ).values_list('id', 'songs__id')

                song_rank = {s_id: i for i, s_id in enumerate(song_ids)}
                valid_relations = [r for r in relations if str(r[1]) in song_rank]
                valid_relations.sort(key=lambda x: song_rank[str(x[1])])

                seen_videos = set()
                ordered_video_ids = []

                for video_id, _ in valid_relations:
                    if video_id not in seen_videos:
                        seen_videos.add(video_id)
                        ordered_video_ids.append(video_id)

                return ordered_video_ids

            return await sync_to_async(fetch)()

        ordered_ids = await get_cached_ids(ids_hash=ids_hash)

        def hydrate_results():
            objs = list(models.PerformanceVideo.objects.filter(id__in=ordered_ids))
            objs.sort(key=lambda x: ordered_ids.index(x.id))
            return objs

        return await sync_to_async(hydrate_results)()

    @strawberry.field
    async def get_project_alternative_versions(
            self,
            project_id: strawberry.ID
    ) -> List[types.Project]:
        """
        Fetches alternative versions linked to a specific project.
        """

        @cache_graphql_query(
            CacheKeys.PROJECT_ALTERNATIVE_VERSIONS,
            timeout=86400,  # ✅ Cached for 24 Hours
            key_params=["project_id"]
        )
        async def get_cached_ids(project_id: strawberry.ID):
            def fetch():
                return list(
                    models.Project.objects.filter(id=project_id)
                    .values_list('alternative_versions__id', flat=True)
                )

            return await sync_to_async(fetch)()

        raw_ids = await get_cached_ids(project_id=project_id)
        clean_ids = [x for x in raw_ids if x is not None]

        def hydrate_results():
            return list(models.Project.objects.filter(id__in=clean_ids))

        return await sync_to_async(hydrate_results)()

    @strawberry.field
    async def get_artist_most_popular_projects(
            self,
            artist_id: strawberry.ID,
            limit: int = 10
    ) -> List[types.Project]:

        @cache_graphql_query(
            CacheKeys.ARTIST_POPULAR_PROJECTS,
            timeout=3600,
            key_params=["artist_id", "limit"]
        )
        async def get_cached_ids(artist_id: strawberry.ID, limit: int):
            def fetch():
                return list(
                    models.Project.objects.filter(
                        project_artists__artist_id=artist_id
                    )
                    .order_by('-popularity_score')
                    .values_list('id', flat=True)[:limit]
                )

            return await sync_to_async(fetch)()

        ordered_ids = await get_cached_ids(artist_id=artist_id, limit=limit)

        def hydrate_results():
            projects = list(models.Project.objects.filter(id__in=ordered_ids))

            projects.sort(key=lambda x: ordered_ids.index(x.id))

            return projects

        return await sync_to_async(hydrate_results)()


    @strawberry.field
    async def match_songs_by_title_and_artists(
            self,
            song_title: str,
            artist_ids: List[str]
    ) -> List[types.Song]:

        if not song_title or not artist_ids:
            return []

        ids_str = ",".join(sorted(artist_ids))

        @cache_graphql_query(
            CacheKeys.MATCH_SONGS,
            timeout=0,
            key_params=["title", "artists_hash"]
        )
        async def get_matched_ids(title: str, artists_hash: str):
            def fetch():
                qs = models.Song.objects.all()
                for artist_id in artist_ids:
                    qs = qs.filter(song_artists__artist__apple_music_id=artist_id)

                return list(
                    qs.annotate(
                        similarity=Greatest(
                            TrigramWordSimilarity(Value(title), F('title')),
                            TrigramWordSimilarity(F('title'), Value(title))
                        )
                    )
                    .filter(similarity__gt=0.6)
                    .order_by('id', '-similarity')
                    .distinct('id')
                    .values_list('id', flat=True)[:20]
                )

            return await sync_to_async(fetch)()

        matched_ids = await get_matched_ids(title=song_title, artists_hash=ids_str)

        def hydrate_results():
            songs = list(models.Song.objects.filter(id__in=matched_ids))
            songs.sort(key=lambda x: matched_ids.index(x.id))
            return songs

        return await sync_to_async(hydrate_results)()

    @strawberry.field
    async def match_projects_by_title_and_artists(
            self,
            project_title: str,
            artist_ids: List[str]
    ) -> List[types.Project]:

        if not project_title or not artist_ids:
            return []

        ids_str = ",".join(sorted(artist_ids))

        @cache_graphql_query(
            CacheKeys.MATCH_PROJECTS,
            timeout=0,
            key_params=["title", "artists_hash"]
        )
        async def get_matched_ids(title: str, artists_hash: str):
            def fetch():
                return list(
                    models.Project.objects.filter(
                        project_artists__artist__apple_music_id__in=artist_ids
                    )
                    .annotate(
                        similarity=Greatest(
                            TrigramWordSimilarity(Value(title), F('title')),
                            TrigramWordSimilarity(F('title'), Value(title))
                        )
                    )
                    .filter(similarity__gt=0.6)
                    .order_by('id', '-similarity')
                    .distinct('id')
                    .values_list('id', flat=True)[:20]
                )

            return await sync_to_async(fetch)()

        matched_ids = await get_matched_ids(title=project_title, artists_hash=ids_str)

        def hydrate_results():
            projects = list(models.Project.objects.filter(id__in=matched_ids))
            projects.sort(key=lambda x: matched_ids.index(x.id))
            return projects

        return await sync_to_async(hydrate_results)()

    @strawberry.field
    async def review_topic_configuration(self) -> List[types.TopicMapping]:
        @cache_graphql_query(
            CacheKeys.REVIEW_TOPIC_CONFIG,
            timeout=86400,
            key_params=[]
        )
        async def get_cached_config():
            def build_config():
                configs = []
                for model_name, topics in models.SubReview.TOPIC_MAPPING.items():
                    configs.append(types.TopicMapping(
                        model_name=model_name,
                        allowed_topics=topics
                    ))
                return configs

            return await sync_to_async(build_config)()

        return await get_cached_config()

    @strawberry.field
    async def search_podcasts(self, query: str) -> types.PodcastSearchResponse:
        if not query:
            return types.PodcastSearchResponse(is_cached=False, podcasts=[])

        limit = 5
        # Update cache key to differentiate this new search logic if needed
        cache_key = make_cache_key(CacheKeys.PODCAST_SEARCH, query=query, type="fuzzy")
        cached_data = await sync_to_async(cache.get)(cache_key)
        was_in_cache = cached_data is not None

        @cache_graphql_query(CacheKeys.PODCAST_SEARCH, timeout=300, key_params=["query"])
        async def get_cached_podcast_ids(query: str):
            def fetch_ids():
                # 1. Annotate a single string containing Title + Host
                # 2. Calculate similarity of that string to the user's query
                return list(
                    models.Podcast.objects.annotate(
                        search_text=Concat('title', Value(' '), 'hosts__name'),
                        similarity=TrigramSimilarity('search_text', query),
                    )
                    # 0.1 is a good starting threshold (10% match).
                    # For "Gagx" vs "Gaga", similarity is ~0.6, so this easily passes.
                    .filter(similarity__gt=0.1)
                    .order_by('-similarity')  # Most similar first
                    .values_list('id', flat=True)[:limit]
                )

            return await sync_to_async(fetch_ids)()

        podcast_ids = await get_cached_podcast_ids(query=query)

        def hydrate_results():
            # We must preserve the specific order returned by the similarity search
            # 'filter(id__in=...)' does not guarantee order, so we sort manually in Python
            objects = list(models.Podcast.objects.filter(id__in=podcast_ids))
            objects.sort(key=lambda x: podcast_ids.index(x.id))
            return types.PodcastSearchResponse(is_cached=was_in_cache, podcasts=objects)

        return await sync_to_async(hydrate_results)()

    @strawberry.field
    async def search_music(self, query: str) -> types.MusicSearchResponse:
        if not query:
            return types.MusicSearchResponse(
                is_cached=False, artists=[], projects=[], songs=[], music_videos=[], performance_videos=[]
            )

        limit = 5
        cache_key = make_cache_key(CacheKeys.MUSIC_SEARCH, query=query, type="fuzzy")
        cached_data = await sync_to_async(cache.get)(cache_key)
        was_in_cache = cached_data is not None

        @cache_graphql_query(CacheKeys.MUSIC_SEARCH, timeout=300, key_params=["query"])
        async def get_cached_search_ids(query: str):
            def fetch_ids():
                # Helper to perform the fuzzy search on a model
                def fuzzy_search(queryset, *field_names):
                    # Combine all fields into one searchable string
                    # e.g. "Bad Romance Lady Gaga"
                    search_expression = field_names[0]
                    for field in field_names[1:]:
                        search_expression = Concat(search_expression, Value(' '), field)

                    return list(
                        queryset.annotate(
                            similarity=TrigramSimilarity(search_expression, query)
                        )
                        .filter(similarity__gt=0.1)  # Threshold: 0.1 to 0.3 is standard
                        .order_by('-similarity')
                        .values_list('id', flat=True)[:limit]
                    )

                return {
                    "artists": fuzzy_search(models.Artist.objects.all(), 'name'),

                    # Search Project Title + Artist Name
                    "projects": fuzzy_search(
                        models.Project.objects.all(),
                        'title', 'project_artists__artist__name'
                    ),

                    # Search Song Title + Artist Name
                    "songs": fuzzy_search(
                        models.Song.objects.all(),
                        'title', 'song_artists__artist__name'
                    ),

                    # Search Music Video Title + Song Title + Artist
                    "music_videos": fuzzy_search(
                        models.MusicVideo.objects.all(),
                        'title', 'songs__title', 'songs__song_artists__artist__name'
                    ),

                    "performance_videos": fuzzy_search(
                        models.PerformanceVideo.objects.all(), 'title'
                    )
                }

            return await sync_to_async(fetch_ids)()

        data_ids = await get_cached_search_ids(query=query)

        def hydrate_results():
            # Helper to fetch and resort objects
            def fetch_and_sort(model, ids):
                objs = list(model.objects.filter(id__in=ids))
                objs.sort(key=lambda x: ids.index(x.id))
                return objs

            return types.MusicSearchResponse(
                is_cached=was_in_cache,
                artists=fetch_and_sort(models.Artist, data_ids["artists"]),
                projects=fetch_and_sort(models.Project, data_ids["projects"]),
                songs=fetch_and_sort(models.Song, data_ids["songs"]),
                music_videos=fetch_and_sort(models.MusicVideo, data_ids["music_videos"]),
                performance_videos=fetch_and_sort(models.PerformanceVideo, data_ids["performance_videos"])
            )

        return await sync_to_async(hydrate_results)()

    @strawberry.field
    async def search_itunes_podcasts(self, term: str) -> List[iTunesPodcastLight]:
        results = await itunes_service.search_podcasts(term)

        result_ids = [podcast.get("collectionId") for podcast in results if podcast.get("collectionId")]

        existing_ids = await sync_to_async(lambda: list(
            models.Podcast.objects.filter(
                apple_podcasts_id__in=result_ids
            ).values_list('apple_podcasts_id', flat=True)
        ))()

        # Convert to a set for O(1) lookup speed
        existing_ids_set = set(existing_ids)
        podcasts: List[iTunesPodcastLight] = []

        for item in results:
            if item.get("collectionId") in existing_ids_set:
                continue
            # Upgrade image quality
            base_image = item.get("artworkUrl600", "") or item.get("artworkUrl100", "")
            high_res_image = get_high_res_artwork(base_image)

            podcasts.append(
                iTunesPodcastLight(
                    id=str(item.get("collectionId")),
                    title=item.get("collectionName", ""),
                    host=item.get("artistName", ""),
                    image_url=high_res_image
                )
            )
        return podcasts

    @strawberry.field
    async def get_youtube_video_by_url(self, url: str) -> YoutubeVideoDetail:
        # 1. Fetch data from service
        vid = await youtube_service.get_video_by_url(url)

        if not vid:
            return None

        video_id = vid.get("id")

        # 2. Check if it already exists in DB (to avoid duplicates or handle logic)
        existing_exists = await sync_to_async(lambda:
            models.MusicVideo.objects.filter(youtube_id=video_id).exists() or
            models.PerformanceVideo.objects.filter(youtube_id=video_id).exists()
        )()

        # If it already exists, you might want to return None or handle as you see fit
        # For now, following your pattern of filtering out existing ones:
        if existing_exists:
            return None

        # 3. Map to GraphQL Type
        return YoutubeVideoDetail(
            id=video_id,
            title=vid.get("title", ""),
            thumbnail_url=vid.get("thumbnail", ""),
            channel_name=vid.get("channel_title", ""),
            published_at=vid.get("published_at", ""),
            length_ms=vid.get("length_ms", 0),
            view_count=vid.get("view_count", "0"),
            url=vid.get("url", ""),
            primary_color=vid.get("primary_color", "#000000")
        )

    @strawberry.field
    async def search_youtube_videos(self, term: str) -> List[YoutubeVideoDetail]:
        results = await youtube_service.search_videos(term)

        result_ids = [video.get("id") for video in results if video.get("id")]

        existing_ids = await sync_to_async(lambda: list(
            models.MusicVideo.objects.filter(
                youtube_id__in=result_ids
            ).values_list('youtube_id', flat=True)
        ) + list(
            models.PerformanceVideo.objects.filter(
                youtube_id__in=result_ids
            ).values_list('youtube_id', flat=True)
        ))()

        existing_ids_set = set(existing_ids)

        videos: List[YoutubeVideoDetail] = []

        for vid in results:
            if vid.get("id") in existing_ids_set:
                continue

            videos.append(
                YoutubeVideoDetail(
                    id=vid.get("id"),
                    title=vid.get("title", ""),
                    thumbnail_url=vid.get("thumbnail", ""),
                    channel_name=vid.get("channel_title", ""),
                    published_at=vid.get("published_at", ""),
                    length_ms=vid.get("length_ms", 0),
                    view_count=vid.get("view_count", 0),
                    url=vid.get("url", ""),
                    primary_color=vid.get("primary_color", "#000000")
                )
            )
        return videos


    @strawberry.field
    async def search_apple_music_albums(self, term: str) -> List[AppleMusicAlbumLight]:
        results = await apple_music.search_albums(term)

        # 1. Extract all Apple Music IDs from the search results
        result_ids = [album.get("id") for album in results if album.get("id")]

        # 2. Check which of these IDs already exist in your Project database
        # We use sync_to_async because accessing Django models is synchronous
        existing_ids = await sync_to_async(lambda: list(
            models.Project.objects.filter(
                apple_music_id__in=result_ids
            ).values_list('apple_music_id', flat=True)
        ))()

        # Convert to a set for O(1) lookup speed
        existing_ids_set = set(existing_ids)

        albums: List[AppleMusicAlbumLight] = []

        for album in results:
            # 3. Skip this album if its ID is already in the database
            if album.get("id") in existing_ids_set:
                continue

            album_attrs = album.get("attributes", {})
            artists_names = album_attrs.get("artistName", "")

            artwork = album_attrs.get("artwork", {})
            cover_url = artwork.get("url", "") if artwork else ""
            primary_color = artwork.get("bgColor", "") if artwork else ""
            secondary_color = artwork.get("textColor1", "") if artwork else ""
            track_count = album_attrs.get("trackCount", 0)
            kind = album_attrs.get("playParams", {}).get("kind", "")
            is_single = album_attrs.get("isSingle", False)
            is_complete = album_attrs.get("isComplete", False)

            albums.append(
                AppleMusicAlbumLight(
                    id=album.get("id"),
                    name=album_attrs.get("name", ""),
                    release_date=album_attrs.get("releaseDate", ""),
                    cover_url=cover_url,
                    primary_color=primary_color,
                    secondary_color=secondary_color,
                    artists_names=artists_names,
                    track_count=track_count,
                    kind=kind,
                    is_single=is_single,
                    is_complete=is_complete,
                )
            )
        return albums

    @strawberry.field
    async def get_album_detail(self, album_id: str) -> AppleMusicAlbumDetail:
        # 1. Fetch the main album object
        album = await apple_music.get_album_with_songs(album_id)
        album_attrs = album.get("attributes", {})

        # ✅ Album Artists (Main artists for the album)
        album_artists: List[AppleMusicArtistDetail] = []
        for artist in album.get("relationships", {}).get("artists", {}).get("data", []):
            artist_href = artist.get("href", "")
            artist_name, artist_image, artist_url = "", "", ""
            artist_genre_names = []

            if artist_href:
                try:
                    artist_detail = await apple_music.get_artist(artist_href)
                    attrs = artist_detail.get("attributes", {})
                    artist_name = attrs.get("name", "")
                    artist_image = attrs.get("artwork", {}).get("url", "")
                    artist_url = attrs.get("url", "")
                    artist_genre_names = attrs.get("genreNames", [])
                except Exception:
                    pass

            album_artists.append(
                AppleMusicArtistDetail(
                    id=artist.get("id"),
                    name=artist_name,
                    image_url=artist_image,
                    url=artist_url,
                    genre_names=artist_genre_names,
                )
            )

        # ✅ Songs
        songs: List[AppleMusicSongDetail] = []
        number_of_songs = 0

        for song in album.get("relationships", {}).get("tracks", {}).get("data", []):
            song_type = song.get("type", "")

            if song_type != "songs":
                continue

            song_href = song.get("href", "")
            song_attrs = song.get("attributes", {})

            # KEY FIX: Check if song is released/playable.
            is_released = song_attrs.get("playParams") is not None

            full_song = None

            # Only fetch full details if the song is actually out
            if is_released and song_href:
                try:
                    full_song = await apple_music.get_song(song_href)
                except Exception:
                    full_song = None

            # ✅ Song Artists Logic
            song_artists: List[AppleMusicArtistDetail] = []

            if full_song:
                # RELEASED: We can get the full Artist object with ID
                for s_artist in full_song.get("relationships", {}).get("artists", {}).get("data", []):
                    try:
                        s_artist_href = s_artist.get("href", "")
                        s_artist_name, s_artist_image, s_artist_url = "", "", ""
                        s_artist_genre_names = []

                        if s_artist_href:
                            s_artist_detail = await apple_music.get_artist(s_artist_href)
                            s_attrs = s_artist_detail.get("attributes", {})
                            s_artist_name = s_attrs.get("name", "")
                            s_artist_image = s_attrs.get("artwork", {}).get("url", "")
                            s_artist_url = s_attrs.get("url", "")
                            s_artist_genre_names = s_attrs.get("genreNames", [])

                        song_artists.append(
                            AppleMusicArtistDetail(
                                id=s_artist.get("id"),
                                name=s_artist_name,
                                image_url=s_artist_image,
                                url=s_artist_url,
                                genre_names=s_artist_genre_names,
                            )
                        )
                    except Exception:
                        continue
            else:
                # UNRELEASED / FALLBACK: Use metadata from the Album's tracklist
                song_artists.append(
                    AppleMusicArtistDetail(
                        id="",  # Valid because id is now Optional[str]
                        name=song_attrs.get("artistName", "Unknown Artist"),
                        image_url="",
                        url="",
                        genre_names=[]
                    )
                )

            # ✅ Add song
            songs.append(
                AppleMusicSongDetail(
                    id=song.get("id"),
                    type=song.get("type", ""),
                    name=song_attrs.get("name", ""),
                    length_ms=song_attrs.get("durationInMillis", 0),
                    disc_number=song_attrs.get("discNumber"),
                    genre_names=song_attrs.get("genreNames", []),
                    preview_url=song_attrs.get("previews", [{}])[0].get("url", "") if is_released else "",
                    artists=song_artists,
                    track_number=song_attrs.get("trackNumber", 0),
                    release_date=song_attrs.get("releaseDate", ""),
                    url=song_attrs.get("url", ""),
                    is_out = is_released,
                )
            )
            number_of_songs += 1

        # ✅ Album cover & metadata
        artwork = album_attrs.get("artwork", {})
        cover_url = artwork.get("url", "") if artwork else ""
        primary_color = artwork.get("bgColor", "") if artwork else ""
        secondary_color = artwork.get("textColor1", "") if artwork else ""
        genre_names = album_attrs.get("genreNames", [])
        kind = album_attrs.get("playParams", {}).get("kind", "")
        url = album_attrs.get("url", "")
        is_single = album_attrs.get("isSingle", False)
        is_compilation = album_attrs.get("isCompilation", False)
        is_complete = album_attrs.get("isComplete", False)
        record_label = album_attrs.get("recordLabel", "")

        return AppleMusicAlbumDetail(
            id=album.get("id"),
            name=album_attrs.get("name", ""),
            release_date=album_attrs.get("releaseDate", ""),
            cover_url=cover_url,
            primary_color=primary_color,
            secondary_color=secondary_color,
            songs=songs,
            artists=album_artists,
            track_count=number_of_songs,
            genre_names=genre_names,
            record_label=record_label,
            kind=kind,
            url=url,
            is_single=is_single,
            is_compilation=is_compilation,
            is_complete=is_complete,
        )

    @strawberry.field
    async def search_apple_music_artists(self, term: str) -> List[AppleMusicArtistLight]:
        results = await apple_music.search_artists(term)
        artists: List[AppleMusicArtistLight] = []

        for artist in results:
            attrs = artist.get("attributes", {})
            artwork = attrs.get("artwork", {})
            image_url = artwork.get("url", "") if artwork else ""

            artists.append(
                AppleMusicArtistLight(
                    id=artist.get("id"),
                    name=attrs.get("name", ""),
                    image_url=image_url
                )
            )
        return artists

    @strawberry.field
    async def get_apple_music_artist_detail(self, artist_id: str) -> AppleMusicArtistDetail:
        artist = await apple_music.get_artist(f"/v1/catalog/us/artists/{artist_id}")
        attrs = artist.get("attributes", {})

        return AppleMusicArtistDetail(
            id=artist.get("id"),
            name=attrs.get("name", ""),
            image_url=attrs.get("artwork", {}).get("url", ""),
            url=attrs.get("url", ""),
            genre_names=attrs.get("genreNames", []),
        )

    @strawberry.field
    async def get_apple_music_artist_top_songs(self, artist_id: str) -> List[AppleMusicSongLight]:
        """
        Fetches the top songs for a given Apple Music Artist ID.
        """
        # 1. Call the new service method
        results = await apple_music.get_artist_top_songs(artist_id)
        songs: List[AppleMusicSongLight] = []

        # 2. Map the results to the GraphQL type
        for song in results:
            song_attrs = song.get("attributes", {})

            songs.append(
                AppleMusicSongLight(
                    id=song.get("id"),
                    name=song_attrs.get("name", ""),
                    length_ms=song_attrs.get("durationInMillis", 0),
                    preview_url=song_attrs.get("previews", [{}])[0].get("url", ""),
                    artists_names=song_attrs.get("artistName", ""),
                    release_date=song_attrs.get("releaseDate", ""),
                )
            )
        return songs

    music_genres: DjangoCursorConnection[types.MusicGenre] = strawberry_django.connection(filters=filters.MusicGenreFilter, order=orders.MusicGenreOrder)
    project_genres_ordered: DjangoCursorConnection[types.ProjectGenresOrdered] = strawberry_django.connection(filters=filters.ProjectGenresOrderedFilter, order=orders.ProjectGenresOrderedOrder)
    song_genres_ordered: DjangoCursorConnection[types.SongGenresOrdered] = strawberry_django.connection(filters=filters.SongGenresOrderedFilter, order=orders.SongGenresOrderedOrder)
    artist_genres_ordered: DjangoCursorConnection[types.ArtistGenresOrdered] = strawberry_django.connection(filters=filters.ArtistGenresOrderedFilter, order=orders.ArtistGenresOrderedOrder)

    podcast_genres: DjangoCursorConnection[types.PodcastGenre] = strawberry_django.connection(filters=filters.PodcastGenreFilter, order=orders.PodcastGenreOrder)
    podcast_genres_ordered: DjangoCursorConnection[types.PodcastGenresOrdered] = strawberry_django.connection(filters=filters.PodcastGenresOrderedFilter, order=orders.PodcastGenresOrderedOrder)

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
    performance_videos: DjangoCursorConnection[types.PerformanceVideo] = strawberry_django.connection(filters=filters.PerformanceVideoFilter, order=orders.PerformanceVideoOrder)
    users: DjangoCursorConnection[types.User] = strawberry_django.connection(filters=filters.UserFilter, order=orders.UserOrder)
    search_history: DjangoCursorConnection[types.SearchHistory] = strawberry_django.connection(filters=filters.SearchHistoryFilter, order=orders.SearchHistoryOrder)

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