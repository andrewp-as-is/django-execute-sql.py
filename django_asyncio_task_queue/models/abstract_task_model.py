from datetime import datetime

from asgiref.sync import sync_to_async
from django.db import models

from .asyncio_task_queue_log import Log

class AbstractTaskModel(models.Model):
    is_completed = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    is_enqueued = models.BooleanField(default=False)
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

    is_logged = None
    exclude_fields = [
        'is_completed',
        'is_disabled',
        'is_enqueued',
        # 'is_restarted',
        'disabled_at',
        'enqueued_at',
        'restarted_at',
        'updated_at'
    ]

    class Meta:
        abstract = True

    def get_db_table(self):
        return self._meta.db_table

    @classmethod
    def get_exclude_fields(model):
        return exclude_fields

    @classmethod
    def get_only_fields(model):
        exclude_fields = model.get_exclude_fields()
        fields = list(filter(lambda f: f.name not in (exclude_fields or []), model._meta.fields))
        return list(map(lambda f: f.name, fields))

    @classmethod
    def get_queryset(model):
        only_fields = model.get_only_fields()
        qs =model.objects.filter(is_completed=False, is_enqueued=False, is_disabled=False)
        if only_fields:
            qs = qs.only(*only_fields)
        return qs.order_by('-priority', 'activated_at')

    async def complete_task(self, **kwargs):
        self.is_completed = True
        duration = str(datetime.now() - self.started_at)[0:7]
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
        await self.log('COMPLETED %s seconds' % duration)

    async def delete_task(self):
        self.is_deleted = True
        await sync_to_async(self.model.objects.filter(pk=pk).delete)()
        await self.log('DELETED')

    async def disable_task(self):
        self.is_disabled = True
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
        await self.log('DISABLED')

    async def restart_task(self, **kwargs):
        self.is_restarted = True
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
        await self.log('RESTARTED')

    async def update_task(self, **kwargs):
        await sync_to_async(self.model.objects.filter(pk=pk).update)(**kwargs)

    async def log(self, msg):
        if self.is_logged:
            await sync_to_async(Log.objects.create)(
                db_table=self._meta.db_table,
                task_id=self.id,
                msg=msg,
                created_at=datetime.now()
            )

    async def save_exc(self):
        exc, exc_value, tb = sys.exc_info()
        await sync_to_async(Exc(
            db_table=self._meta.db_table,
            task_id=self.id,
            exc_type=exc.__module__ + '.' + exc.__name__ if exc.__module__ else exc.__name__,
            exc_value=exc_value if exc_value else '',
            exc_traceback='\n'.join(format_tb(tb))
        ).save)()
