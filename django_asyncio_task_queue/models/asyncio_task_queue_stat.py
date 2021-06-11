from .abstract_stat import AbstractStat

class Stat(AbstractStat):

    class Meta:
        db_table = 'asyncio_task_queue_stat'
        ordering = ('db_table',)
        verbose_name_plural = "Stat"
