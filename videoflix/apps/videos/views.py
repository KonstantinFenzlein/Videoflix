from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Video, Genre
from .serializers import VideoListSerializer, VideoDetailSerializer, GenreSerializer

class VideoViewSet(ReadOnlyModelViewSet):
    # Stellt eine Read-Only API für Videos mit Filterung nach Genre bereit.
    queryset = Video.objects.prefetch_related('qualities').select_related('genre')
    permission_classes = [IsAuthenticated]
    filterset_fields = ['genre']

    def get_serializer_class(self):
        # Gibt den passenden Serializer je nach Aktion zurück (Listenansicht oder Detail).
        if self.action == 'retrieve':
            return VideoDetailSerializer
        return VideoListSerializer

class GenreViewSet(ReadOnlyModelViewSet):
    # Stellt eine Read-Only API für alle verfügbaren Genres bereit.
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticated]
