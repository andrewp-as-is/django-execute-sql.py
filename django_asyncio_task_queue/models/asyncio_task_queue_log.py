from django.db import models


class Log(models.Model):
    db_table = models.TextField()
    task_id = models.IntegerField()

    msg = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'asyncio_task_queue_log'
