import strawberry
import strawberry_django
from strawberry import auto
from STARS import models
from django.contrib.auth.models import User
from typing import Optional

# Define an order for the base User model first, so we can reuse it
@strawberry_django.order_type(User)
class UserOrder:
    username : auto
    first_name : auto
    email : auto
    is_active : auto
    followed_by_current_user: auto
    reviews: Optional["ReviewOrder"]

@strawberry_django.order_type(models.MusicGenre)
class MusicGenreOrder:
    title: auto
    is_featured : auto

@strawberry_django.order_type(models.Artist)
class ArtistOrder:
    name : auto
    birthdate : auto
    is_featured : auto

@strawberry_django.order_type(models.EventSeries)
class EventSeriesOrder:
    name : auto
    is_featured : auto

@strawberry_django.order_type(models.Event)
class EventOrder:
    date : auto
    name : auto
    is_one_time :  auto
    reviews_count : auto
    star_average : auto
    is_featured : auto

@strawberry_django.order_type(models.Comment)
class CommentOrder:
    date_created : auto
    likes_count : auto
    dislikes_count : auto

@strawberry_django.order_type(models.Review)
class ReviewOrder:
    date_created : auto
    stars : auto
    comments_count : auto
    likes_count : auto
    dislikes_count : auto
    is_latest : auto
    user_followed_by_current_user: auto

@strawberry_django.order_type(models.SubReview)
class SubReviewOrder:
    stars : auto
    position : auto
    topic : auto

@strawberry_django.order_type(models.Cover)
class CoverOrder:
    position : auto
    star_average : auto
    reviews_count : auto
    is_featured : auto

@strawberry_django.order_type(models.MusicVideo)
class MusicVideoOrder:
    release_date : auto
    title : auto
    number_of_songs : auto
    reviews_count : auto
    star_average : auto
    is_featured : auto

@strawberry_django.order_type(models.Song)
class SongOrder:
    release_date : auto
    title : auto
    length : auto
    reviews_count : auto
    star_average : auto
    is_featured : auto

@strawberry_django.order_type(models.SongArtist)
class SongArtistOrder:
    position : auto

@strawberry_django.order_type(models.Project)
class ProjectOrder:
    release_date : auto
    title : auto
    length : auto
    number_of_songs : auto
    project_type : auto
    reviews_count : auto
    star_average : auto
    is_featured : auto

@strawberry_django.order_type(models.ProjectArtist)
class ProjectArtistOrder:
    position : auto

@strawberry_django.order_type(models.ProjectSong)
class ProjectSongOrder:
    position : auto
    disc_number: auto

@strawberry_django.order_type(models.Podcast)
class PodcastOrder:
    since : auto
    title : auto
    reviews_count : auto
    star_average : auto
    is_featured : auto

@strawberry_django.order_type(models.Outfit)
class OutfitOrder:
    date : auto
    reviews_count : auto
    star_average : auto
    is_featured : auto

@strawberry_django.order_type(models.Conversation)
class ConversationOrder:
    latest_message_time : auto
    latest_message_sender : auto

@strawberry_django.order_type(models.Message)
class MessageOrder:
    time : auto

@strawberry_django.order_type(models.Profile)
class ProfileOrder:
    user : UserOrder
    has_premium : auto
    followers_count : auto
    following_count : auto
    reviews_count : auto
    project_reviews_count : auto
    song_reviews_count : auto
    music_video_reviews_count : auto
    cover_reviews_count : auto
    podcast_reviews_count : auto
    outfit_reviews_count : auto