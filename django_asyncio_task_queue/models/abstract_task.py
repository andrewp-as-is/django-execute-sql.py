from django.db import models

class AbstractTaskModel(models.Model):
    activated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)
    disabled_at = models.DateTimeField(null=True)
    enqueued_at = models.DateTimeField(null=True)
    restarted_at = models.DateTimeField(null=True)
    started_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    is_completed = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    is_enqueued = models.BooleanField(default=False)
    is_restarted = models.BooleanField(default=False)

    priority = models.IntegerField(default=0, null=False)

    class Meta:
        abstract = True

    def get_db_table(self):
        return self._meta.db_table
