from .abstract_error import AbstractError

class Error(AbstractError):

    class Meta:
        db_table = 'asyncio_task_queue_error'
