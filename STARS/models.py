# STARS/models.py
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db.models import JSONField


class Artist(models.Model):
    apple_music_id = models.CharField(blank=True, null=True, max_length=255)
    name = models.CharField(max_length=100, db_index=True)
    picture = models.URLField(max_length=500)
    bio = models.TextField(blank=True)
    wikipedia = models.URLField(max_length=500, blank=True, null=True)
    pronouns = models.CharField(max_length=100, blank=True)
    birthdate = models.DateField(blank=True, null=True)
    origin = models.CharField(max_length=200, blank=True)
    website = models.URLField(max_length=500, blank=True, null=True)
    facebook = models.URLField(max_length=500, blank=True, null=True)
    instagram = models.URLField(max_length=500, blank=True, null=True)
    twitter = models.URLField(max_length=500, blank=True, null=True)
    youtube_channel = models.URLField(max_length=500, blank=True, null=True)
    spotify = models.URLField(max_length=500, blank=True, null=True)
    apple_music = models.URLField(max_length=500, blank=True, null=True)
    youtube_music = models.URLField(max_length=500, blank=True, null=True)
    tidal = models.URLField(max_length=500, blank=True, null=True)
    deezer = models.URLField(max_length=500, blank=True, null=True)
    soundcloud = models.URLField(max_length=500, blank=True, null=True)
    bandcamp = models.URLField(max_length=500, blank=True, null=True)
    projects_star_average = models.FloatField(default=0)
    songs_star_average = models.FloatField(default=0)
    music_videos_star_average = models.FloatField(default=0)
    performances_star_average = models.FloatField(default=0)
    covers_star_average = models.FloatField(default=0)
    outfits_star_average = models.FloatField(default=0)
    is_featured = models.BooleanField(default=False, db_index=True)
    featured_message = models.TextField(blank=True)

    primary_color = models.CharField(max_length=7, blank=True)  # e.g., "#FF5733"
    secondary_color = models.CharField(max_length=7, blank=True)  # e.g., "#33A1FF"

    def __str__(self):
        return self.name


class EventSeries(models.Model):
    class EventType(models.TextChoices):
        AWARD_SHOW = "AWARD_SHOW", "Award Show"
        TOUR = "TOUR", "Tour"
        FESTIVAL = "FESTIVAL", "Festival"
        TV_APPEARANCE = "TV_SHOW", "TV Show"
        LIVE_SESSION = "LIVE_SESSION", "Live Session"
        RESIDENCY = "RESIDENCY", "Residency"
        OTHER = "OTHER", "Other"

    series_type = models.CharField(max_length=20, choices=EventType.choices, db_index=True, default=EventType.OTHER)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    picture = models.URLField(max_length=500, null=True, blank=True)
    star_average = models.FloatField(default=0)
    is_featured = models.BooleanField(default=False, db_index=True)
    featured_message = models.TextField(blank=True)

    primary_color = models.CharField(max_length=7, blank=True)  # e.g., "#FF5733"
    secondary_color = models.CharField(max_length=7, blank=True)  # e.g., "#33A1FF"

    def __str__(self):
        return self.name


class Event(models.Model):
    class EventType(models.TextChoices):
        AWARD_SHOW = "AWARD_SHOW", "Award Show"
        TOUR = "TOUR", "Tour"
        FESTIVAL = "FESTIVAL", "Festival"
        TV_APPEARANCE = "TV_SHOW", "TV Show"
        LIVE_SESSION = "LIVE_SESSION", "Live Session"
        RESIDENCY = "RESIDENCY", "Residency"
        OTHER = "OTHER", "Other"

    event_type = models.CharField(max_length=25, choices=EventType.choices, db_index=True, default=EventType.OTHER)

    series = models.ForeignKey('EventSeries', on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    name = models.CharField(max_length=255, db_index=True)
    date = models.DateField(blank=True, null=True)
    picture = models.URLField(max_length=500, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    is_one_time = models.BooleanField(default=False)
    reviews_count = models.IntegerField(default=0)
    reviews = GenericRelation('Review')
    star_average = models.FloatField(default=0)
    popularity_score = models.IntegerField(default=0, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    featured_message = models.TextField(blank=True)

    primary_color = models.CharField(max_length=7, blank=True)  # e.g., "#FF5733"
    secondary_color = models.CharField(max_length=7, blank=True)  # e.g., "#33A1FF"

    def clean(self):
        if not self.name:
            raise ValidationError({'name': 'Events must have a name.'})
        if not self.event_type:
            raise ValidationError({'event_type': 'Events must have an event type.'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.date})"


class Comment (models.Model):
    review = models.ForeignKey('Review', on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    number_of_replies = models.IntegerField(default=0)
    replying_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    likes_count = models.IntegerField(default=0)
    dislikes_count = models.IntegerField(default=0)
    liked_by = models.ManyToManyField(User, blank=True, related_name='liked_comments')
    disliked_by = models.ManyToManyField(User, blank=True, related_name='disliked_comments')

    def __str__(self):
        return f"Comment from {self.user.username} saying {self.text}"


class RankedList(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RankedList {self.pk}"


class RankedItem(models.Model):
    ranked_list = models.ForeignKey(RankedList, on_delete=models.CASCADE, related_name='items')
    position = models.PositiveIntegerField()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    description = models.TextField(blank=True)

    class Meta:
        ordering = ['position']
        unique_together = ('ranked_list', 'position')

    def __str__(self):
        return f"{self.position}. {self.content_object} in Ranked List {self.ranked_list_id}"


class Review(models.Model):
    stars = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    title = models.CharField(max_length=255, blank=True)

    text = models.TextField(blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_latest = models.BooleanField(default=True)
    comments_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    dislikes_count = models.IntegerField(default=0)
    liked_by = models.ManyToManyField(User, blank=True, related_name='liked_reviews')
    disliked_by = models.ManyToManyField(User, blank=True, related_name='disliked_reviews')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    ranked_list = models.OneToOneField(RankedList, null=True, blank=True, on_delete=models.SET_NULL, related_name='review')

    class Meta:
        ordering = ['-date_created']

    def clean(self):
        super().clean()

        if self.content_type or self.object_id:
            if self.stars is None:
                raise ValidationError("Reviews must have a star rating.")
            if not self.title:
                raise ValidationError("Reviews must have a title.")

        else:
            if not self.text:
                raise ValidationError("Posts must have text content.")

    @property
    def is_post(self):
        return self.content_type is None

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.content_object:
            return f"Review by {self.user.username} on {self.content_object}"
        return f"Post by {self.user.username}: {self.text[:30]}"


class SubReview(models.Model):
    class Topic(models.TextChoices):
        LYRICS = "LYRICS", "Lyrics"
        PRODUCTION = "PRODUCTION", "Production"
        COLOR_PALETTE = "COLOR_PALETTE", "Color Palette"
        DIRECTION = "DIRECTION", "Direction"
        VOCAL_PERFORMANCE = "VOCAL_PERFORMANCE", "Vocal Performance"
        STYLING = "STYLING", "Styling"

    TOPIC_MAPPING = {
        'song': [Topic.LYRICS, Topic.PRODUCTION, Topic.VOCAL_PERFORMANCE],
        'project': [Topic.LYRICS, Topic.PRODUCTION],
        'cover': [Topic.COLOR_PALETTE],
        'outfit': [Topic.COLOR_PALETTE, Topic.STYLING],
        'musicvideo': [Topic.COLOR_PALETTE, Topic.DIRECTION],
    }

    review = models.ForeignKey('Review', on_delete=models.CASCADE, related_name='subreviews')
    topic = models.CharField(max_length=50, choices=Topic.choices)
    text = models.TextField(blank=True)
    stars = models.DecimalField(max_digits=3, decimal_places=2)
    position = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['position']

    def clean(self):
        super().clean()
        if not self.review or not self.review.content_type:
            return

        model_name = self.review.content_type.model.lower()
        allowed_topics = self.TOPIC_MAPPING.get(model_name, [])

        if self.topic and self.topic not in allowed_topics:
            raise ValidationError(
                f"Topic '{self.topic}' is not a valid option for a {model_name} review."
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Subreview of {self.review} – {self.topic}"


class Cover(models.Model):
    image = models.URLField(max_length=500, unique=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    position = models.PositiveIntegerField(default=1)
    reviews_count = models.IntegerField(default=0)
    reviews = GenericRelation('Review')
    star_average = models.FloatField(default=0)
    popularity_score = models.IntegerField(default=0, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    featured_message = models.TextField(blank=True)

    primary_color = models.CharField(max_length=7, blank=True)  # e.g., "#FF5733"
    secondary_color = models.CharField(max_length=7, blank=True)  # e.g., "#33A1FF"

    class Meta:
        unique_together = ('content_type', 'object_id', 'position')

    def __str__(self):
        return f"Cover for {self.content_object} ({self.image})"


class MusicVideo(models.Model):
    youtube_id = models.CharField(blank=True, null=True, max_length=255, unique=True)
    title = models.CharField(max_length=500, db_index=True)
    channel_name = models.CharField(max_length=500, db_index=True)
    number_of_songs = models.IntegerField()
    songs = models.ManyToManyField('Song', related_name='music_videos')
    release_date = models.DateField(db_index=True)
    length = models.IntegerField()
    youtube = models.URLField(max_length=500, unique=True)
    thumbnail = models.URLField(max_length=500, null=True, blank=True)
    reviews_count = models.IntegerField(default=0)
    reviews = GenericRelation('Review')
    star_average = models.FloatField(default=0)
    popularity_score = models.IntegerField(default=0, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    featured_message = models.TextField(blank=True)

    primary_color = models.CharField(max_length=7, blank=True)  # e.g., "#FF5733"
    secondary_color = models.CharField(max_length=7, blank=True)  # e.g., "#33A1FF"

    def __str__(self):
        return self.title


class PerformanceVideo(models.Model):
    youtube_id = models.CharField(blank=True, null=True, max_length=255, unique=True)
    title = models.CharField(max_length=500, db_index=True)
    artists = models.ManyToManyField('Artist', related_name='performance_videos')
    event = models.ForeignKey('Event', on_delete=models.SET_NULL, related_name='performance_videos', null=True)
    channel_name = models.CharField(max_length=500, db_index=True)
    number_of_songs = models.IntegerField()
    songs = models.ManyToManyField('Song', related_name='performance_videos')
    release_date = models.DateField(db_index=True)
    length = models.IntegerField()
    youtube = models.URLField(max_length=500, unique=True)
    thumbnail = models.URLField(max_length=500, null=True, blank=True)
    reviews_count = models.IntegerField(default=0)
    reviews = GenericRelation('Review')
    star_average = models.FloatField(default=0)
    popularity_score = models.IntegerField(default=0, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    featured_message = models.TextField(blank=True)

    primary_color = models.CharField(max_length=7, blank=True)  # e.g., "#FF5733"
    secondary_color = models.CharField(max_length=7, blank=True)  # e.g., "#33A1FF"

    def __str__(self):
        return self.title


class Song(models.Model):
    apple_music_id = models.CharField(blank=True, null=True, max_length=255, unique=True)
    title = models.CharField(max_length=500, db_index=True)
    length = models.IntegerField()
    preview = models.URLField(max_length=500, blank=True, null=True)
    release_date = models.DateField(db_index=True)
    is_out = models.BooleanField(default=True, db_index=True)
    reviews_count = models.IntegerField(default=0)
    reviews = GenericRelation('Review')
    star_average = models.FloatField(default=0)
    popularity_score = models.IntegerField(default=0, db_index=True)
    alternative_versions = models.ManyToManyField('self', blank=True)
    spotify = models.URLField(max_length=500, blank=True, null=True)
    apple_music = models.URLField(max_length=500, blank=True, null=True)
    youtube_music = models.URLField(max_length=500, blank=True, null=True)
    tidal = models.URLField(max_length=500, blank=True, null=True)
    deezer = models.URLField(max_length=500, blank=True, null=True)
    soundcloud = models.URLField(max_length=500, blank=True, null=True)
    bandcamp = models.URLField(max_length=500, blank=True, null=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    featured_message = models.TextField(blank=True)

    def __str__(self):
        release_info = self.release_date if self.is_out else "Unreleased"
        return f"{self.title} - {release_info}"


class SongArtist(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='song_artists')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='song_artists')
    position = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.song.title} - {self.position}. {self.artist.name}"

    class Meta:
        ordering = ['position']
        unique_together = (
            ('song', 'artist'),
            ('song', 'position'),
        )


class Project(models.Model):
    class ProjectType(models.TextChoices):
        ALBUM = "ALBUM", "Album"
        EP = "EP", "EP"
        MIXTAPE = "MIXTAPE", "Mixtape"
        SINGLE = "SINGLE", "Single"

    apple_music_id = models.CharField(blank=True, null=True, max_length=255, unique=True)
    title = models.CharField(max_length=500, db_index=True)
    length = models.IntegerField()
    number_of_songs = models.IntegerField()
    release_date = models.DateField(db_index=True)
    project_type = models.CharField(max_length=10, choices=ProjectType.choices, db_index=True)
    covers = GenericRelation('Cover')
    record_label = models.CharField(max_length=500, null = True, blank = True, db_index=True)
    reviews = GenericRelation('Review')
    reviews_count = models.IntegerField(default=0)
    star_average = models.FloatField(default=0)
    popularity_score = models.IntegerField(default=0, db_index=True)
    alternative_versions = models.ManyToManyField('self', blank=True)
    spotify = models.URLField(max_length=500, blank=True, null=True)
    apple_music = models.URLField(max_length=500, blank=True, null=True)
    youtube_music = models.URLField(max_length=500, blank=True, null=True)
    tidal = models.URLField(max_length=500, blank=True, null=True)
    deezer = models.URLField(max_length=500, blank=True, null=True)
    soundcloud = models.URLField(max_length=500, blank=True, null=True)
    bandcamp = models.URLField(max_length=500, blank=True, null=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    featured_message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} - {self.release_date}"


class ProjectArtist(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_artists') # <-- ADDED
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='project_artists') # <-- ADDED
    position = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.project.title} - {self.position}. {self.artist.name}"

    class Meta:
        ordering = ['position']
        unique_together = (
            ('project', 'artist'),
            ('project', 'position'),
        )


class ProjectSong(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_songs') # <-- ADDED
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='project_songs') # <-- ADDED
    position = models.PositiveIntegerField()
    disc_number = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.project.title} - {self.position}. {self.song.title}"

    class Meta:
        ordering = ['disc_number', 'position']
        unique_together = (
            ('project', 'song'),
            ('project', 'disc_number', 'position'),
        )


class Podcast(models.Model):
    apple_podcasts_id = models.CharField(blank=True, null=True, max_length=255, unique=True)
    title = models.CharField(max_length=500, db_index=True)
    host = models.CharField(max_length=500, db_index=True)
    description = models.TextField(blank=True)
    since = models.DateField(db_index=True)
    covers = GenericRelation('Cover')
    website = models.URLField(max_length=500, blank=True, null=True)
    spotify = models.URLField(max_length=500, blank=True, null=True)
    apple_podcasts = models.URLField(max_length=500, blank=True, null=True)
    youtube = models.URLField(max_length=500, blank=True, null=True)
    youtube_music = models.URLField(max_length=500, blank=True, null=True)
    reviews_count = models.IntegerField(default=0)
    reviews = GenericRelation('Review')
    star_average = models.FloatField(default=0)
    popularity_score = models.IntegerField(default=0, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    featured_message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} - {self.host}"


class Outfit(models.Model):
    artist = models.ForeignKey('Artist', on_delete=models.SET_NULL, related_name='outfits', null = True)
    description = models.TextField(blank=True)
    date = models.DateField(db_index=True)
    events = models.ManyToManyField('Event', blank=True, related_name='outfits')
    music_videos = models.ManyToManyField('MusicVideo', blank=True, related_name='outfits')
    covers = models.ManyToManyField('Cover', blank=True, related_name='outfits')
    preview_picture = models.URLField(max_length=500)
    instagram_post = models.URLField(max_length=500)
    reviews_count = models.IntegerField(default=0)
    reviews = GenericRelation('Review')
    star_average = models.FloatField(default=0)
    popularity_score = models.IntegerField(default=0, db_index=True)
    matches = models.ManyToManyField('self', blank=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    featured_message = models.TextField(blank=True)

    primary_color = models.CharField(max_length=7, blank=True)  # e.g., "#FF5733"
    secondary_color = models.CharField(max_length=7, blank=True)  # e.g., "#33A1FF"

    def __str__(self):
        artist_name = self.artist.name if self.artist else "Unknown Artist"
        short_desc = self.description[:40] + "..." if len(self.description) > 40 else self.description
        return f"{artist_name} – {short_desc} ({self.date})"


class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    latest_message = models.ForeignKey('Message', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    latest_message_text = models.TextField(blank=True)
    latest_message_time = models.DateTimeField(null=True, blank=True)
    latest_message_sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='latest_sent_conversations')
    seen_by = models.ManyToManyField(User, blank=True, related_name='seen_conversations')

    color = models.CharField(max_length=7, blank=True)  # e.g., "#FF5733"

    class Meta:
        ordering = ['-latest_message_time']

    def __str__(self):
        users = ', '.join(user.username for user in self.participants.all())
        return f"Conversation between {users}"


class Message(models.Model):
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='sent_messages', null=True)
    text = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    is_delivered = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    liked_by = models.ManyToManyField(User, blank=True, related_name='liked_messages')
    replying_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')

    class Meta:
        ordering = ['time']

    def __str__(self):
        return f"Message #{self.pk} from {self.sender.username} at {self.time}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    has_premium = models.BooleanField(default=False)
    banner_picture = models.URLField(max_length=500, blank=True, null=True)
    profile_picture = models.URLField(max_length=500, blank=True, null=True)
    bio = models.TextField(blank=True)
    pronouns = models.CharField(max_length=100, blank=True)
    followers_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    reviews_count = models.IntegerField(default=0)
    project_reviews_count = models.IntegerField(default=0)
    song_reviews_count = models.IntegerField(default=0)
    music_video_reviews_count = models.IntegerField(default=0)
    performance_video_reviews_count = models.IntegerField(default=0)
    cover_reviews_count = models.IntegerField(default=0)
    podcast_reviews_count = models.IntegerField(default=0)
    outfit_reviews_count = models.IntegerField(default=0)

    custom_primary_color = models.CharField(max_length=7, blank=True)  # e.g., "#FF5733"
    custom_secondary_color = models.CharField(max_length=7, blank=True)  # e.g., "#33A1FF"
    profile_picture_primary_color = models.CharField(max_length=7, blank=True)  # e.g., "#FF5733"
    profile_picture_secondary_color = models.CharField(max_length=7, blank=True)  # e.g., "#33A1FF"
    banner_picture_primary_color = models.CharField(max_length=7, blank=True)  # e.g., "#FF5733"
    banner_picture_secondary_color = models.CharField(max_length=7, blank=True)  # e.g., "#33A1FF"

    def __str__(self):
        return f"Profile of {self.user.username}"


class SearchHistory(models.Model):
    class SearchCategory(models.TextChoices):
        MUSIC = "MUSIC", "Music"
        PODCAST = "PODCAST", "Podcast"
        OUTFIT = "OUTFIT", "Outfit"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    query = models.CharField(max_length=255)
    category = models.CharField(
        max_length=10,
        choices=SearchCategory.choices,
        db_index=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} searched '{self.query}' in {self.category}"


class MusicGenre(models.Model):
    title = models.CharField(max_length=500, db_index=True, unique=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    featured_message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} - {self.is_featured}"

    class Meta:
        ordering = ['title']


class ProjectGenresOrdered(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_genres_ordered')
    genre = models.ForeignKey(MusicGenre, on_delete=models.CASCADE, related_name='project_genres_ordered')
    position = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.project.title} - {self.position}. {self.genre.title}"

    class Meta:
        ordering = ['position']
        unique_together = (
            ('project', 'genre'),
            ('project', 'position'),
        )


class SongGenresOrdered(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='song_genres_ordered')
    genre = models.ForeignKey(MusicGenre, on_delete=models.CASCADE, related_name='song_genres_ordered')
    position = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.song.title} - {self.position}. {self.genre.title}"

    class Meta:
        ordering = ['position']
        unique_together = (
            ('song', 'genre'),
            ('song', 'position'),
        )


class ArtistGenresOrdered(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='artist_genres_ordered')
    genre = models.ForeignKey(MusicGenre, on_delete=models.CASCADE, related_name='artist_genres_ordered')
    position = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.artist.name} - {self.position}. {self.genre.title}"

    class Meta:
        ordering = ['position']
        unique_together = (
            ('artist', 'genre'),
            ('artist', 'position'),
        )


class PodcastGenre(models.Model):
    title = models.CharField(max_length=500, db_index=True, unique=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    featured_message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} - {self.is_featured}"

    class Meta:
        ordering = ['title']


class PodcastGenresOrdered(models.Model):
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE, related_name='podcast_genres_ordered')
    genre = models.ForeignKey(PodcastGenre, on_delete=models.CASCADE, related_name='podcast_genres_ordered')
    position = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.podcast.title} - {self.position}. {self.genre.title}"

    class Meta:
        ordering = ['position']
        unique_together = (
            ('podcast', 'genre'),
            ('podcast', 'position'),
        )


class UnresolvedImportTask(models.Model):
    class TaskStatus(models.TextChoices):
        PENDING_USER = "PENDING_USER", "Awaiting User Resolution"
        PENDING_ADMIN = "PENDING_ADMIN", "Awaiting Admin Review"
        RESOLVED = "RESOLVED", "Task Completed"

    # The user who initiated the import
    importer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='import_tasks')

    # What the task is about
    task_type = models.CharField(max_length=50, choices=[('DEDUPLICATION', 'Song Deduplication'),
                                                         ('FEATURE_RESOLUTION', 'Feature Resolution')])

    # The external ID of the original project (Apple Music Album ID)
    external_id = models.CharField(max_length=255, db_index=True)

    # JSON field to store the specific data needed for resolution
    # (e.g., {song_id: "...", candidates: [...]})
    resolution_payload = JSONField()

    # Current status of the task
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.PENDING_USER, db_index=True)

    # When the task was created (used for automated escalation)
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_updated = models.DateTimeField(auto_now=True)

    # Optional link to the partially created Project in STARS DB
    partial_project = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True)

    # Optional admin note/resolution log
    admin_note = models.TextField(blank=True)

    def __str__(self):
        return f"Task for {self.task_type} on {self.external_id} - {self.get_status_display()}"