from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Artist, Project, Song, ProjectSong, Podcast, Outfit, Review, SubReview, Profile, Message, Conversation, Event, EventSeries, Cover, MusicVideo, ProjectArtist, SongArtist, Comment, MusicGenre, UnresolvedImportTask  # etc.

admin.site.register(Artist)
admin.site.register(Project)
admin.site.register(Song)
admin.site.register(Podcast)
admin.site.register(Outfit)
admin.site.register(Review)
admin.site.register(SubReview)
admin.site.register(Profile)
admin.site.register(Message)
admin.site.register(Conversation)
admin.site.register(Event)
admin.site.register(EventSeries)
admin.site.register(Cover)
admin.site.register(MusicVideo)
admin.site.register(ProjectSong)
admin.site.register(ProjectArtist)
admin.site.register(SongArtist)
admin.site.register(Comment)
admin.site.register(MusicGenre)
admin.site.register(UnresolvedImportTask)