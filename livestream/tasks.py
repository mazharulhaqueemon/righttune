from celery import shared_task
from django.utils import timezone
from .models import LiveStreaming

@shared_task
def reset_stream_priorities():
    now = timezone.now()
    streams_to_reset = LiveStreaming.objects.filter(end_time__lte=now)
    for stream in streams_to_reset:
        stream.priority = 0
        stream.end_time = None
        stream.save()