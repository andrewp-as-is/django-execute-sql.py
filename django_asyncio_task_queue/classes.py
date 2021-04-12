from datetime import datetime

from asgiref.sync import sync_to_async
from django.db.utils import InterfaceError, OperationalError

from .models import Log


class TaskRunner:
    model = None

    def __init__(self, **kwargs):
        self.is_completed = False
        self.is_deleted = False
        self.is_disabled = False
        self.is_logged = False
        self.is_restarted = False
        for k, v in kwargs.items():
            setattr(self, k, v)
        await self.log('CREATED')

    async def log(self, msg):
        if self.is_logged:
            await sync_to_async(Log.objects.create)(
                db_table=self.model._meta.db_table,
                task_id=self.id,
                msg=msg,
                created_at=datetime.now()
            )

    async def run(self):
        pass

    async def run_finally(self):
        pass

    async def complete_task(self, **kwargs):
        self.is_completed = True
        duration = str(datetime.now() - self.started_at)[0:7]
        await self.log('COMPLETED time %s seconds' % duration)
        completed_at = datetime.now()
        kwargs.update(
            is_completed=True,
            is_disabled=False,
            is_enqueued=False,
            is_restarted=False,
            completed_at=completed_at,
            disabled_at=None,
            restarted_at=None,
            started_at=self.started_at,
            updated_at=datetime.now()
        )
        await self.update_task(**kwargs)

    async def delete_task(self):
        self.is_deleted = True
        await self.log('DELETED')
        await sync_to_async(self.model.objects.filter(pk=pk).delete)()

    async def disable_task(self):
        self.is_disabled = True
        await self.log('DISABLED')
        kwargs = dict(
            is_completed=False,
            is_disabled=True,
            is_enqueued=False,
            is_restarted=False,
            completed_at=None,
            disabled_at=datetime.now(),
            enqueued_at=None,
            restarted_at=None,
            started_at=None,
            updated_at=datetime.now()
        )
        await self.update_task(**kwargs)

    async def restart_task(self, **kwargs):
        self.is_restarted = True
        await self.log('RESTARTED')
        kwargs.update(
            disabled_at=None,
            enqueued_at=None,
            is_completed=False,
            is_disabled=False,
            is_enqueued=False,
            is_restarted=True,
            restarted_at=datetime.now(),
            started_at=None,
            updated_at=datetime.now()
        )
        await self.update_task(**kwargs)

    async def update_task(self, **kwargs):
        await sync_to_async(self.model.objects.filter(pk=pk).update)(**kwargs)
