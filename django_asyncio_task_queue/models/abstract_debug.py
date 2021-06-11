from django.db import models

class AbstractDebug(models.Model):
    db_table = models.TextField()
    task_id = models.TextField()

    msg = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
