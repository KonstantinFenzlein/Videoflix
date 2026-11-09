from rest_framework.exceptions import APIException
from rest_framework import status


class InvalidResolutionError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Ungültige Auflösung.'
    default_code = 'invalid_resolution'


class ResolutionNotAvailableError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Auflösung nicht verfügbar.'
    default_code = 'resolution_not_available'


class PlaylistNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Playlist-Datei nicht gefunden.'
    default_code = 'playlist_not_found'


class SegmentNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Segment nicht gefunden.'
    default_code = 'segment_not_found'


class FileReadError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Fehler beim Lesen der Datei.'
    default_code = 'file_read_error'
