import django_rq
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Video
from .tasks import process_video

# HLS-Konvertierung mehrerer Qualitäten kann länger als der Standard-Timeout (900 s) dauern.
PROCESSING_JOB_TIMEOUT = 3600

@receiver(pre_save, sender=Video)
def remember_video_file_change(sender, instance, **kwargs):
    # Merkt sich, ob die Videodatei neu oder geändert wurde, bevor das Modell gespeichert wird.
    if instance.pk is None:
        instance._video_file_changed = True
        return
    stored_name = Video.objects.filter(pk=instance.pk).values_list('video_file', flat=True).first()
    instance._video_file_changed = stored_name != instance.video_file.name

@receiver(post_save, sender=Video)
def enqueue_video_processing(sender, instance, created, **kwargs):
    # Startet die HLS-Konvertierung im Hintergrund, sobald eine neue oder geänderte Videodatei committed ist.
    if created or getattr(instance, '_video_file_changed', False):
        transaction.on_commit(
            lambda: django_rq.enqueue(process_video, instance.id, job_timeout=PROCESSING_JOB_TIMEOUT)
        )
