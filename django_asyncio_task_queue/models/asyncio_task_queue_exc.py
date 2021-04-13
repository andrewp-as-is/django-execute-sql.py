from .abstract_exc import AbstractExc

class Exc(AbstractExc):

    class Meta:
        db_table = 'asyncio_task_queue_exc'
