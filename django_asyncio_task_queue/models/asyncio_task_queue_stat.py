from .abstract_stat import AbstractStat

class Stat(AbstractStat):

    class Meta:
        db_table = 'asyncio_task_queue_stat'
