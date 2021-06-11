from .abstract_error import AbstractError

class Error(AbstractError):

    class Meta:
        db_table = 'asyncio_task_queue_error'
        ordering = ('-created_at',)
        verbose_name_plural = "Error"
