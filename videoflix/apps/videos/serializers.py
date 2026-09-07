from rest_framework import serializers
from .models import Video, Genre, VideoQuality

class GenreSerializer(serializers.ModelSerializer):
    # Serialisiert Genre-Daten für die API.
    class Meta:
        model = Genre
        fields = ('id', 'name', 'description')

class VideoQualitySerializer(serializers.ModelSerializer):
    # Serialisiert Video-Qualitätsdaten mit Playlist-Links.
    class Meta:
        model = VideoQuality
        fields = ('id', 'quality', 'playlist_file')

class VideoListSerializer(serializers.ModelSerializer):
    # Serialisiert Video-Listenansicht mit Titel und Miniaturansicht.
    genre = GenreSerializer(read_only=True)

    class Meta:
        model = Video
        fields = ('id', 'title', 'thumbnail', 'genre', 'created_at')

class VideoDetailSerializer(serializers.ModelSerializer):
    # Serialisiert detaillierte Video-Informationen mit allen verfügbaren Qualitäten.
    genre = GenreSerializer(read_only=True)
    qualities = VideoQualitySerializer(read_only=True, many=True)

    class Meta:
        model = Video
        fields = ('id', 'title', 'description', 'genre', 'thumbnail', 'duration', 'qualities', 'created_at')
