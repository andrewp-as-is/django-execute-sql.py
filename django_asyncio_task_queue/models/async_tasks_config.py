from django.db import models


class Config(models.Model):
    db_table = models.TextField(null=True)
    is_logged = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    limit = models.IntegerField()

    class Meta:
        db_table = 'async_tasks_config'
        managed = False
