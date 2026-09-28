from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.conf import settings
import os
import re
import logging
from .models import Video, Genre, VideoQuality
from .serializers import VideoListSerializer, VideoDetailSerializer, GenreSerializer
from .exceptions import (
    InvalidResolutionError, ResolutionNotAvailableError,
    PlaylistNotFoundError, SegmentNotFoundError, FileReadError
)

logger = logging.getLogger(__name__)

ALLOWED_RESOLUTIONS = {'480p', '720p', '1080p'}

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

    @action(detail=True, methods=['get'], url_path='stream/(?P<resolution>[\\w]+)')
    def stream(self, request, pk=None, resolution=None):
        # Liefert die HLS-Master-Playlist für eine bestimmte Auflösung.
        if resolution not in ALLOWED_RESOLUTIONS:
            logger.warning(f'Invalid resolution requested: {resolution}')
            raise InvalidResolutionError(
                detail=f'Ungültige Auflösung. Erlaubte Werte: {", ".join(sorted(ALLOWED_RESOLUTIONS))}'
            )

        video = self.get_object()
        try:
            quality = VideoQuality.objects.get(video=video, quality=resolution)
        except VideoQuality.DoesNotExist:
            logger.info(f'Resolution {resolution} not available for video {video.id}')
            raise ResolutionNotAvailableError()

        if not quality.playlist_file:
            logger.error(f'Playlist file missing for video {video.id} resolution {resolution}')
            raise PlaylistNotFoundError()

        try:
            logger.info(f'Streaming playlist: video_id={video.id}, resolution={resolution}, user={request.user.id}')
            f = quality.playlist_file.open('rb')
            response = FileResponse(f, content_type='application/vnd.apple.mpegurl')
            response['Content-Disposition'] = f'inline; filename="{video.id}_{resolution}.m3u8"'
            response['Cache-Control'] = 'public, max-age=3600'
            return response
        except IOError as e:
            logger.error(f'Error reading playlist file: video_id={video.id}, resolution={resolution}, error={str(e)}')
            raise FileReadError()

    @action(detail=True, methods=['get'], url_path='stream/(?P<resolution>\\w+)/(?P<segment>[\\w.-]+\\.ts)')
    def segment(self, request, pk=None, resolution=None, segment=None):
        # Liefert ein einzelnes HLS-Videosegment.
        if not segment or not re.match(r'^[\w.-]+\.ts$', segment):
            logger.warning(f'Invalid segment filename requested: {segment}')
            raise SegmentNotFoundError(detail='Ungültiger Segment-Dateiname.')

        if resolution not in ALLOWED_RESOLUTIONS:
            logger.warning(f'Invalid resolution requested: {resolution}')
            raise InvalidResolutionError(
                detail=f'Ungültige Auflösung. Erlaubte Werte: {", ".join(sorted(ALLOWED_RESOLUTIONS))}'
            )

        video = self.get_object()
        try:
            quality = VideoQuality.objects.get(video=video, quality=resolution)
        except VideoQuality.DoesNotExist:
            logger.info(f'Resolution {resolution} not available for video {video.id}')
            raise ResolutionNotAvailableError()

        if not quality.playlist_file:
            logger.error(f'Playlist file missing for video {video.id} resolution {resolution}')
            raise PlaylistNotFoundError()

        try:
            playlist_dir = os.path.dirname(quality.playlist_file.path)
            segment_path = os.path.join(playlist_dir, segment)
            segment_real_path = os.path.realpath(segment_path)
            playlist_real_dir = os.path.realpath(playlist_dir)

            if not segment_real_path.startswith(playlist_real_dir):
                logger.warning(f'Possible directory traversal attempt: {segment_path}')
                raise SegmentNotFoundError()

            if not os.path.exists(segment_real_path):
                logger.warning(f'Segment file not found: {segment_real_path}')
                raise SegmentNotFoundError()

            logger.info(f'Streaming segment: video_id={video.id}, resolution={resolution}, segment={segment}, user={request.user.id}')
            f = open(segment_real_path, 'rb')
            response = FileResponse(f, content_type='video/MP2T')
            response['Content-Disposition'] = f'inline; filename="{segment}"'
            response['Cache-Control'] = 'public, max-age=86400'
            return response
        except IOError as e:
            logger.error(f'Error reading segment file: video_id={video.id}, segment={segment}, error={str(e)}')
            raise FileReadError()

class GenreViewSet(ReadOnlyModelViewSet):
    # Stellt eine Read-Only API für alle verfügbaren Genres bereit.
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticated]
