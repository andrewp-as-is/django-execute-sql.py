from django.db import models

class AbstractError(models.Model):
    db_table = models.TextField()
    task_id = models.TextField()

    exc_type = models.TextField()
    exc_value = models.TextField()
    exc_traceback = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
