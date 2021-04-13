from .abstract_config import AbstractConfig

class Config(AbstractConfig):

    class Meta:
        db_table = 'asyncio_task_queue_config'
