from django.apps import AppConfig
from django.db.utils import ImproperlyConfigured, OperationalError, ProgrammingError


class Config(AppConfig):
    name = 'django_asyncio_task_queue'
    verbose_name = 'asyncio-task-queue'

    def ready(self):
        from .models import Debug, Error

        try:
            Debug._meta.verbose_name_plural = 'Debug (%s)' % Debug.objects.all().count()
            Error._meta.verbose_name_plural = 'Error (%s)' % Error.objects.all().count()
        except (ImproperlyConfigured,OperationalError,ProgrammingError):
            pass

