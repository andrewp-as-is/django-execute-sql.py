from django.db import models


class AbstractStat(models.Model):
    db_table = models.TextField(unique=True)
    tasks_count = models.IntegerField()
    completed_tasks_count = models.IntegerField()
    pending_tasks_count = models.IntegerField()
    enqueued_tasks_count = models.IntegerField()
    restarted_tasks_count = models.IntegerField()
    disabled_tasks_count = models.IntegerField()
    exc_count = models.IntegerField()
    logs_count = models.IntegerField()
    updated_at = models.DateTimeField(null=True)

    class Meta:
        abstract = True

