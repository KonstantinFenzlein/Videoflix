from pathlib import Path
from django.conf import settings
from videoflix.utils.video import convert_video_to_hls
from .models import Video, VideoQuality

HLS_QUALITIES = ['480p', '720p', '1080p']

def process_video(video_id):
    # Konvertiert das hochgeladene Video in HLS-Playlists und legt die Qualitätsstufen an.
    video = Video.objects.get(id=video_id)
    output_dir = Path(settings.MEDIA_ROOT) / 'hls' / str(video.id)
    convert_video_to_hls(video.video_file.path, output_dir, HLS_QUALITIES)

    for quality in HLS_QUALITIES:
        VideoQuality.objects.update_or_create(
            video=video,
            quality=quality,
            defaults={'playlist_file': f'hls/{video.id}/{quality}/playlist.m3u8'}
        )
