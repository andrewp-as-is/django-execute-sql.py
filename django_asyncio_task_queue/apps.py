from django.apps import AppConfig

from django_async_tasks.utils import register_tasks

class Config(AppConfig):
    name = 'django_async_tasks'

    def ready(self):
        register_tasks([])


"""
todo docs
"""
