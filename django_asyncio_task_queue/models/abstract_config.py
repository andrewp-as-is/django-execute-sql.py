from django.db import models


class AbstractConfig(models.Model):
    db_table = models.TextField(null=True)
    is_logged = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    enqueue_limit = models.IntegerField(default=42)

    class Meta:
        abstract = True
