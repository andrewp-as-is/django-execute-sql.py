from django.db import models


class Stat(models.Model):
    db_table = models.TextField(unique=True)
    count = models.IntegerField()
    completed_count = models.IntegerField()
    pending_count = models.IntegerField()
    enqueued_count = models.IntegerField()
    restarted_count = models.IntegerField()
    disabled_count = models.IntegerField()
    is_disabled = models.BooleanField(default=False)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'async_tasks_stat'
        managed = False
