from .abstract_log import AbstractLog

class Log(AbstractLog):

    class Meta:
        db_table = 'asyncio_task_queue_log'
