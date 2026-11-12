from django.db import models
from django.core.validators import FileExtensionValidator

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'genre'
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'
        ordering = ['name']

    def __str__(self):
        # Gibt den Namen des Genres zurück.
        return self.name

class Video(models.Model):
    # Speichert Video-Metadaten einschließlich Titel, Beschreibung, Miniaturansicht und Videodatei.
    title = models.CharField(max_length=200)
    description = models.TextField()
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    thumbnail = models.ImageField(upload_to='thumbnails/')
    video_file = models.FileField(upload_to='videos/', validators=[FileExtensionValidator(allowed_extensions=['mp4'])])
    duration = models.IntegerField(help_text='Duration in seconds')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'video'
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'
        ordering = ['-created_at']

    def __str__(self):
        # Gibt den Titel des Videos zurück.
        return self.title

class VideoQuality(models.Model):
    # Speichert HLS-Playlist-Dateien für verschiedene Video-Qualitätsstufen.
    QUALITY_CHOICES = [
        ('480p', '480p'),
        ('720p', '720p'),
        ('1080p', '1080p'),
    ]
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='qualities')
    quality = models.CharField(max_length=10, choices=QUALITY_CHOICES)
    playlist_file = models.FileField(upload_to='hls/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'video_quality'
        verbose_name = 'Video Quality'
        verbose_name_plural = 'Video Qualities'
        unique_together = ['video', 'quality']

    def __str__(self):
        # Gibt Videotitel und Qualitätsstufe zurück.
        return f"{self.video.title} - {self.quality}"
