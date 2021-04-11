from django.db import models
from django_postgres_timestamp_without_tz import DateTimeWithoutTZField


class Log(models.Model):
    db_table = models.TextField()
    task_id = models.IntegerField()

    msg = models.TextField()
    created_at = DateTimeWithoutTZField(auto_now_add=True)

    class Meta:
        db_table = 'async_tasks_log'
