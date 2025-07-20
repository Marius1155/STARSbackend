from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation

class Artist(models.Model):
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
    is_featured = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return self.name


class EventSeries(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    series = models.ForeignKey('EventSeries', on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    name = models.CharField(max_length=255)
    date = models.DateField()
    location = models.CharField(max_length=255, blank=True)
    is_one_time = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"{self.name} ({self.date})"


class Review(models.Model):
    stars = models.DecimalField(max_digits=3, decimal_places=2)
    text = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews') # CASCADE or SET_NULL ?? ... I really don't know what to say
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_latest = models.BooleanField(default=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"Review by {self.user.username} on {self.content_object}"


class SubReview(models.Model):
    review = models.ForeignKey('Review', on_delete=models.CASCADE, related_name='subreviews')
    topic = models.CharField(max_length=255)
    text = models.TextField(blank=True)
    stars = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return f"Subreview of {self.review} – {self.topic}"


class Cover(models.Model):
    image = models.URLField(max_length=500)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    reviews_count = models.IntegerField(default=0)
    reviews = GenericRelation('Review')
    star_average = models.FloatField(default=0)
    is_featured = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"Cover for {self.content_object} ({self.image})"

class MusicVideo(models.Model):
    title = models.CharField(max_length=500, db_index=True)
    songs = models.ManyToManyField('Song', related_name='music_videos')
    releaseDate = models.DateField(db_index=True)
    youtubeURL = models.URLField(max_length=500)
    reviews_count = models.IntegerField(default=0)
    reviews = GenericRelation('Review')
    star_average = models.FloatField(default=0)
    is_featured = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return self.title


class Song(models.Model):
    title = models.CharField(max_length=500, db_index=True)
    length = models.IntegerField()
    preview = models.URLField(max_length=500, blank=True, null=True)
    release_date = models.DateField(db_index=True)
    reviews_count = models.IntegerField(default=0)
    reviews = GenericRelation('Review')
    star_average = models.FloatField(default=0)
    alternative_versions = models.ManyToManyField('self', blank=True)
    is_featured = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"{self.title} - {self.release_date}"

PROJECT_TYPE_CHOICES = [
    ('album', 'Album'),
    ('ep', 'EP'),
    ('mixtape', 'Mixtape'),
    ('single', 'Single'),
]

class SongArtist(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.position}. {self.artist.name} - {self.song.title}"

    class Meta:
        ordering = ['position']
        unique_together = ('song', 'artist')


class Project(models.Model):
    title = models.CharField(max_length=500, db_index=True)
    number_of_songs = models.IntegerField()
    release_date = models.DateField(db_index=True)
    type = models.CharField(max_length=50, choices=PROJECT_TYPE_CHOICES, db_index=True)
    covers = GenericRelation('Cover')
    length = models.IntegerField()
    reviews = GenericRelation('Review')
    reviews_count = models.IntegerField(default=0)
    star_average = models.FloatField(default=0)
    alternative_versions = models.ManyToManyField('self', blank=True)
    spotify = models.URLField(max_length=500, blank=True, null=True)
    apple_music = models.URLField(max_length=500, blank=True, null=True)
    youtube_music = models.URLField(max_length=500, blank=True, null=True)
    tidal = models.URLField(max_length=500, blank=True, null=True)
    deezer = models.URLField(max_length=500, blank=True, null=True)
    soundcloud = models.URLField(max_length=500, blank=True, null=True)
    bandcamp = models.URLField(max_length=500, blank=True, null=True)
    is_featured = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"{self.title} - {self.release_date}"


class ProjectArtist(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.position}. {self.artist.name} - {self.project.title}"

    class Meta:
        ordering = ['position']
        unique_together = ('project', 'artist')


class ProjectSong(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.position}. {self.song.title} - {self.project.title}"

    class Meta:
        ordering = ['position']
        unique_together = ('project', 'song')

class Podcast(models.Model):
    title = models.CharField(max_length=500, db_index=True)
    hosts = models.ManyToManyField('Artist', related_name='podcasts')
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
    is_featured = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        hosts_names = ', '.join(host.name for host in self.hosts.all())
        return f"{self.title} - {hosts_names}"


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
    matches = models.ManyToManyField('self', blank=True)
    is_featured = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        artist_name = self.artist.name if self.artist else "Unknown Artist"
        short_desc = self.description[:40] + "..." if len(self.description) > 40 else self.description
        return f"{artist_name} – {short_desc} ({self.date})"


class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')

    latest_message = models.ForeignKey(
        'Message',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )
    latest_message_text = models.TextField(blank=True)
    latest_message_time = models.DateTimeField(null=True, blank=True)
    latest_message_sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='latest_sent_conversations'
    )

    def __str__(self):
        users = ', '.join(user.username for user in self.participants.all())
        return f"Conversation between {users}"


class Message(models.Model):
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='sent_messages', null=True)
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='received_messages', null=True)

    text = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    is_pending = models.BooleanField(default=True)
    is_delivered = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)

    liked_by = models.ManyToManyField(User, blank=True, related_name='liked_messages')

    replying_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')

    def __str__(self):
        return f"Message #{self.pk} from {self.sender.username} to {self.receiver.username}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hasPremium = models.BooleanField(default=False)
    bannerPicture = models.URLField(max_length=500, blank=True, null=True)
    profilePicture = models.URLField(max_length=500, blank=True, null=True)
    bio = models.TextField(blank=True)
    pronouns = models.CharField(max_length=100, blank=True)
    accentColorHex = models.CharField(max_length=7, blank=True)

    followersCount = models.IntegerField(default=0)
    followingCount = models.IntegerField(default=0)
    followers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='following',
        blank=True
    )

    reviews_count = models.IntegerField(default=0)
    project_reviews_count = models.IntegerField(default=0)
    song_reviews_count = models.IntegerField(default=0)
    music_video_reviews_count = models.IntegerField(default=0)
    cover_reviews_count = models.IntegerField(default=0)
    podcast_reviews_count = models.IntegerField(default=0)
    outfit_reviews_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Profile of {self.user.username}"

