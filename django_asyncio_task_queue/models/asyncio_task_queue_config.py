from django.db import models


class Config(models.Model):
    db_table = models.TextField(null=True)
    is_logged = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    enqueue_limit = models.IntegerField(default=42)

    class Meta:
        db_table = 'asyncio_task_queue_config'
