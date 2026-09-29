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
    # Serialisiert Video-Listenansicht mit allen Metadaten.
    thumbnail_url = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return obj.thumbnail.url if obj.thumbnail else None

    def get_category(self, obj):
        return obj.genre.name if obj.genre else None

    class Meta:
        model = Video
        fields = ('id', 'created_at', 'title', 'description', 'thumbnail_url', 'category')

class VideoDetailSerializer(serializers.ModelSerializer):
    # Serialisiert detaillierte Video-Informationen mit allen verfügbaren Qualitäten.
    genre = GenreSerializer(read_only=True)
    qualities = VideoQualitySerializer(read_only=True, many=True)
    thumbnail_url = serializers.SerializerMethodField()

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return obj.thumbnail.url if obj.thumbnail else None

    class Meta:
        model = Video
        fields = ('id', 'title', 'description', 'genre', 'thumbnail_url', 'duration', 'qualities', 'created_at')
