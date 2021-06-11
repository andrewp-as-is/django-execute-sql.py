from django.db import models

class AbstractStat(models.Model):
    db_table = models.TextField(primary_key=True)
    tasks_count = models.IntegerField(null=True,verbose_name='all')
    pending_tasks_count = models.IntegerField(null=True,verbose_name='pending')
    enqueued_tasks_count = models.IntegerField(null=True,verbose_name='enqueued')
    completed_tasks_count = models.IntegerField(null=True,verbose_name='completed')
    failed_tasks_count = models.IntegerField(null=True,verbose_name='failed')
    disabled_tasks_count = models.IntegerField(null=True,verbose_name='disabled')

    errors_count = models.IntegerField(null=True,verbose_name='errors')
    debug_messages_count = models.IntegerField(null=True,verbose_name='debug')
    updated_at = models.DateTimeField(null=True)

    class Meta:
        abstract = True

