import subprocess
import os
from pathlib import Path

def convert_video_to_hls(video_path, output_dir, qualities):
    # Konvertiert ein Video in HLS-Format mit verschiedenen Qualitätsstufen.
    for quality in qualities:
        resolution = get_resolution(quality)
        output_path = Path(output_dir) / f"{quality}" / "playlist.m3u8"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        command = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f'scale={resolution}',
            '-c:a', 'aac',
            '-c:v', 'libx264',
            '-hls_time', '10',
            '-hls_playlist_type', 'vod',
            str(output_path),
        ]

        subprocess.run(command, check=True)

def get_resolution(quality):
    # Gibt die Bildschirmauflösung für die angeforderte Qualität zurück.
    resolutions = {'480p': '854:480', '720p': '1280:720', '1080p': '1920:1080'}
    return resolutions.get(quality, '1280:720')

def extract_thumbnail(video_path, output_path, timestamp='00:00:05'):
    # Extrahiert einen einzelnen Frame aus einem Video als Vorschaubild.
    command = [
        'ffmpeg',
        '-ss', timestamp,
        '-i', video_path,
        '-vframes', '1',
        '-q:v', '2',
        str(output_path),
    ]
    subprocess.run(command, check=True)
