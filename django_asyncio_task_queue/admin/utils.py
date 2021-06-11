import django.apps
from django_asyncio_task_queue.models import Debug, Error

def set_verbose_name_plural():
    Debug._meta.verbose_name_plural = 'Debug (%s)' % Debug.objects.all().count()
    Error._meta.verbose_name_plural = 'Errors (%s)' % Error.objects.all().count()
