from .abstract_debug import AbstractDebug

class Debug(AbstractDebug):

    class Meta:
        db_table = 'asyncio_task_queue_debug'
