import tempfile
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from videoflix.apps.users.models import CustomUser
from videoflix.apps.videos.models import Genre, Video, VideoQuality
from videoflix.apps.videos.tasks import process_video


class TempMediaMixin:
    # Leitet MEDIA_ROOT pro Test in ein temporäres Verzeichnis um.
    # response.close() schließt nach Django-Logik die DB-Verbindung, wenn sie nicht in einer
    # Transaktion steckt. In TestCase ist das immer der Fall, deshalb wird das hier unterbunden.
    def setUp(self):
        media = tempfile.TemporaryDirectory()
        self.addCleanup(media.cleanup)
        media_override = override_settings(MEDIA_ROOT=media.name)
        media_override.enable()
        self.addCleanup(media_override.disable)
        connection_patch = patch('django.db.backends.base.base.BaseDatabaseWrapper.close_if_unusable_or_obsolete')
        connection_patch.start()
        self.addCleanup(connection_patch.stop)
        super().setUp()


def create_video(title, genre):
    # Legt ein Video mit Dateinamen an. Die Dateien selbst werden nicht benötigt.
    return Video.objects.create(
        title=title,
        description='Testbeschreibung',
        genre=genre,
        thumbnail=f'thumbnails/{title}.jpg',
        video_file=f'videos/{title}.mp4',
        duration=60,
    )


class VideoApiTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='anna@example.com', password='x', username='anna@example.com')
        self.action = Genre.objects.create(name='Action')
        self.drama = Genre.objects.create(name='Drama')
        self.action_video = create_video('explosion', self.action)
        self.drama_video = create_video('liebe', self.drama)

    def authenticated_client(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        return client

    def test_list_requires_authentication(self):
        response = APIClient().get(reverse('videos:video-list'))

        self.assertEqual(response.status_code, 401)

    def test_genre_filter_limits_results(self):
        response = self.authenticated_client().get(reverse('videos:video-list'), {'genre': self.action.id})

        self.assertEqual(response.status_code, 200)
        titles = [item['title'] for item in response.data['results']]
        self.assertEqual(titles, ['explosion'])

    def test_detail_exposes_only_protected_stream_url(self):
        VideoQuality.objects.create(video=self.action_video, quality='480p', playlist_file='hls/1/480p/playlist.m3u8')

        response = self.authenticated_client().get(reverse('videos:video-detail', kwargs={'pk': self.action_video.id}))

        quality = response.data['qualities'][0]
        self.assertNotIn('playlist_file', quality)
        self.assertTrue(quality['stream_url'].endswith(f'/api/videos/videos/{self.action_video.id}/stream/480p/'))

    def test_unknown_resolution_is_rejected(self):
        url = f'/api/videos/videos/{self.action_video.id}/stream/4k/'

        response = self.authenticated_client().get(url)

        self.assertEqual(response.status_code, 400)


class StreamingTests(TempMediaMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.user = CustomUser.objects.create_user(email='anna@example.com', password='x', username='anna@example.com')
        self.video = create_video('film', Genre.objects.create(name='Sci-Fi'))
        self.playlist_dir = Path(settings.MEDIA_ROOT) / 'hls' / str(self.video.id) / '720p'
        self.playlist_dir.mkdir(parents=True)
        (self.playlist_dir / 'playlist.m3u8').write_text('#EXTM3U\n', encoding='utf-8')
        (self.playlist_dir / 'playlist0.ts').write_bytes(b'\x47')
        VideoQuality.objects.create(
            video=self.video,
            quality='720p',
            playlist_file=f'hls/{self.video.id}/720p/playlist.m3u8',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.base_url = f'/api/videos/videos/{self.video.id}/stream/720p/'

    def test_playlist_is_served_with_private_cache_header(self):
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Cache-Control'], 'private, max-age=3600')
        response.close()

    def test_segment_is_served_with_private_cache_header(self):
        response = self.client.get(self.base_url + 'playlist0.ts/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Cache-Control'], 'private, max-age=86400')
        response.close()

    def test_segment_is_served_without_trailing_slash(self):
        response = self.client.get(self.base_url + 'playlist0.ts')

        self.assertEqual(response.status_code, 200)
        response.close()

    def test_missing_segment_returns_404(self):
        response = self.client.get(self.base_url + 'fehlt.ts/')

        self.assertEqual(response.status_code, 404)


class VideoProcessingTests(TempMediaMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.video = create_video('doku', Genre.objects.create(name='Doku'))

    @patch('videoflix.apps.videos.signals.django_rq.enqueue')
    def test_new_video_enqueues_processing_after_commit(self, enqueue):
        with self.captureOnCommitCallbacks(execute=True):
            create_video('neu', None)

        enqueue.assert_called_once()
        args, kwargs = enqueue.call_args
        self.assertEqual(args[0], process_video)
        self.assertEqual(kwargs['job_timeout'], 3600)

    @patch('videoflix.apps.videos.signals.django_rq.enqueue')
    def test_changed_video_file_enqueues_processing(self, enqueue):
        with self.captureOnCommitCallbacks(execute=True):
            self.video.video_file = 'videos/neu.mp4'
            self.video.save()

        enqueue.assert_called_once()

    @patch('videoflix.apps.videos.signals.django_rq.enqueue')
    def test_updating_video_does_not_enqueue(self, enqueue):
        with self.captureOnCommitCallbacks(execute=True):
            self.video.title = 'geaendert'
            self.video.save()

        enqueue.assert_not_called()

    @patch('videoflix.apps.videos.tasks.convert_video_to_hls')
    def test_process_video_creates_all_qualities(self, convert):
        process_video(self.video.id)

        convert.assert_called_once()
        qualities = VideoQuality.objects.filter(video=self.video).order_by('quality')
        self.assertEqual([q.quality for q in qualities], ['1080p', '480p', '720p'])
        self.assertEqual(qualities[0].playlist_file.name, f'hls/{self.video.id}/1080p/playlist.m3u8')

    @patch('videoflix.apps.videos.tasks.convert_video_to_hls')
    def test_process_video_is_idempotent(self, convert):
        process_video(self.video.id)
        process_video(self.video.id)

        self.assertEqual(VideoQuality.objects.filter(video=self.video).count(), 3)


class ThumbnailTests(TempMediaMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.user = CustomUser.objects.create_user(email='anna@example.com', password='x', username='anna@example.com')
        self.video = create_video('poster', Genre.objects.create(name='Drama'))
        thumbnail_dir = Path(settings.MEDIA_ROOT) / 'thumbnails'
        thumbnail_dir.mkdir(parents=True)
        (thumbnail_dir / 'poster.jpg').write_bytes(b'\xff\xd8\xff')
        self.url = f'/api/videos/videos/{self.video.id}/thumbnail/'

    def test_thumbnail_requires_authentication(self):
        response = APIClient().get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_thumbnail_is_served_to_authenticated_user(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.get(self.url)
        content = b''.join(response.streaming_content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Cache-Control'], 'private, max-age=86400')
        self.assertEqual(content, b'\xff\xd8\xff')

    def test_thumbnail_url_points_to_api_endpoint(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.get(f'/api/videos/videos/{self.video.id}/')

        self.assertTrue(response.data['thumbnail_url'].endswith(self.url))
