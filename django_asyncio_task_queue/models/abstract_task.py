from datetime import datetime

from asgiref.sync import sync_to_async
from django.db import models

from .asyncio_task_queue_config import Config
from .asyncio_task_queue_error import Error

CONFIGS = {}

class AbstractTask(models.Model):
    is_completed = models.BooleanField(default=False)
    is_debug = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    is_enqueued = models.BooleanField(default=False)
    is_failed = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=True)
    is_restarted = models.BooleanField(default=False)

    priority = models.IntegerField(default=0, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)
    disabled_at = models.DateTimeField(null=True)
    enqueued_at = models.DateTimeField(null=True)
    restarted_at = models.DateTimeField(null=True)
    started_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        abstract = True

    def get_db_table(self):
        return self._meta.db_table

    async def complete_task(self, **kwargs):
        self.is_completed = True
        self.completed_at = datetime.now()
        duration = str(self.completed_at - self.started_at)[0:7] if self.started_at else None
        await self.debug(''.join(['COMPLETED',': %s' % duration if duration else '']))
        kwargs.update(
            is_completed=True,
            is_disabled=False,
            is_enqueued=False,
            is_pending=False,
            is_restarted=False,
            completed_at=completed_at,
            disabled_at=None,
            restarted_at=None,
            started_at=self.started_at
        )
        await self.update_task(**kwargs)

    async def delete_task(self,msg=None):
        self.is_deleted = True
        await sync_to_async(type(self).objects.filter(id=self.id).delete)()
        await self.debug(''.join(['DELETED',': %s' % msg if msg else '']))

    async def disable_task(self,msg=None):
        self.is_disabled = True
        kwargs = dict(
            is_completed=False,
            is_disabled=True,
            is_enqueued=False,
            is_pending=False,
            is_restarted=False,
            completed_at=None,
            disabled_at=datetime.now(),
            enqueued_at=None,
            restarted_at=None,
            started_at=None
        )
        await self.update_task(**kwargs)
        await self.debug(''.join(['DISABLED',': %s' % msg if msg else '']))

    async def restart_task(self, msg=None,**kwargs):
        self.is_restarted = True
        kwargs.update(
            disabled_at=None,
            enqueued_at=None,
            is_completed=False,
            is_disabled=False,
            is_enqueued=False,
            is_pending=True,
            is_restarted=True,
            restarted_at=datetime.now(),
            started_at=None
        )
        await self.update_task(**kwargs)
        await self.debug(''.join(['RESTARTED',': %s' % msg if msg else '']))

    async def start_task(self, **kwargs):
        self.started_at = datetime.now()
        await self.update_task(started_at=self.started_at,**kwargs)
        await self.debug('STARTED')

    async def update_task(self, **kwargs):
        kwargs.update(updated_at=datetime.now())
        await sync_to_async(type(self).objects.filter(id=self.id).update)(**kwargs)

    async def debug(self, msg):
        for config in CONFIG_LIST:
            if config.db_table == self._meta.db_table and not config.is_debug:
                return
        if self.is_debug:
            await sync_to_async(Debug.objects.create)(
                db_table=self._meta.db_table,
                task_id=self.id,
                msg=msg,
                created_at=datetime.now()
            )

    async def error(self,e):
        await sync_to_async(Error(
            db_table=self._meta.db_table,
            task_id=self.id,
            exc_type='.'.join([type(e).__module__ or 'builtins',type(e).__name__]),
            exc_value=str(e),
            exc_traceback='\n'.join(e.__traceback__)
        ).save)()

    @classmethod
    async def get_queryset(model):
        return model.objects.filter(
            is_completed=False, is_enqueued=False, is_disabled=False
        ).order_by('-priority', 'activated_at')

    @classmethod
    async def put_tasks(model,q):
        if model._meta.db_table not in CONFIGS:
            CONFIGS[model._meta.db_table], created = sync_to_async(Config.objects.get_or_create)(
                db_table=model._meta.db_table
            )
        config = CONFIGS[model._meta.db_table]
        if config.is_disabled:
            return
        enqueued_count = await sync_to_async(model.objects.filter(is_enqueued=True).count)()
        unenqueued_count =config.enqueue_limit - enqueued_count
        if unenqueued_count <= 0:
            return
        task_ids = []
        for task in model.get_queryset()[0:count]:
            q.put_nowait(task)
            task_ids.append(task.id)
        if task_ids:
            await sync_to_async(model.objects.filter(id__in=task_ids).update)(
                is_enqueued=True, enqueued_at=datetime.now()
            )
        return list(task_ids)
