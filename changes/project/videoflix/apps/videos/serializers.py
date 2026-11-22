from django.urls import reverse
from rest_framework import serializers
from .models import Video, Genre, VideoQuality

def build_thumbnail_url(video, request=None):
    # Vorschaubilder laufen über den authentifizierten Endpoint, nicht über /media/.
    path = reverse('videos:video-thumbnail', kwargs={'pk': video.pk}).rstrip('/') + '/'
    return request.build_absolute_uri(path) if request else path

class GenreSerializer(serializers.ModelSerializer):
    # Serialisiert Genre-Daten für die API.
    class Meta:
        model = Genre
        fields = ('id', 'name', 'description')

class VideoQualitySerializer(serializers.ModelSerializer):
    # Serialisiert Video-Qualitätsdaten. Die Playlist wird nur über den geschützten Stream-Endpoint geliefert.
    stream_url = serializers.SerializerMethodField()

    def get_stream_url(self, obj):
        # Kanonische Form mit abschließendem Slash (der Router akzeptiert beide).
        path = reverse('videos:video-stream', kwargs={'pk': obj.video_id, 'resolution': obj.quality}).rstrip('/') + '/'
        request = self.context.get('request')
        return request.build_absolute_uri(path) if request else path

    class Meta:
        model = VideoQuality
        fields = ('id', 'quality', 'stream_url')

class VideoListSerializer(serializers.ModelSerializer):
    # Serialisiert Video-Listenansicht mit allen Metadaten.
    thumbnail_url = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    def get_thumbnail_url(self, obj):
        return build_thumbnail_url(obj, self.context.get('request'))

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
        return build_thumbnail_url(obj, self.context.get('request'))

    class Meta:
        model = Video
        fields = ('id', 'title', 'description', 'genre', 'thumbnail_url', 'duration', 'qualities', 'created_at')
