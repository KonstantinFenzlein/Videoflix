from django.contrib import admin
from .models import Video, Genre, VideoQuality

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'duration', 'created_at')
    list_filter = ('genre', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(VideoQuality)
class VideoQualityAdmin(admin.ModelAdmin):
    list_display = ('video', 'quality', 'created_at')
    list_filter = ('quality', 'created_at')
    search_fields = ('video__title',)
