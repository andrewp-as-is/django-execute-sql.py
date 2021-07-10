from django.apps import apps
from django.db import models

class Model(models.Model):
    app_label = models.CharField(max_length=255)
    label = models.CharField(max_length=255,unique=True)

    is_enabled = models.BooleanField(default=True,verbose_name='enabled')
    push_limit = models.IntegerField(default=42)

    class Meta:
        db_table = 'django_asyncio_task_queue_model'
        ordering = ('label',)

    def get_model(self):
        return apps.get_model(*self.label.split('.'))
