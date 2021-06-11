from datetime import datetime
import importlib
import logging
import os
import sys
import traceback

from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import models

from .asyncio_task_queue_config import Config
from .asyncio_task_queue_debug import Debug
from .asyncio_task_queue_error import Error

CONFIGS = {}

class AbstractTask(models.Model):
    is_enqueued = models.BooleanField(default=False,verbose_name='enqueued')

    class Meta:
        abstract = True

    def get_db_table(self):
        return self._meta.db_table

    async def run_task(self):
        try:
            await self.run_task_try()
        except Exception as e:
            try:
                await self.run_task_except(e)
            except Exception as e:
                print('exc')
                print(''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
                logging.error(e)
        finally:
            try:
                await self.run_task_finally()
            except Exception as e:
                print('exc')
                print(''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
                logging.error(e)

    def get_module_name(self):
        return

    def get_module(self):
        name = self.get_module_name()
        if name:
            if name not in sys.modules:
                return importlib.import_module(name)
            return sys.modules[name]

    async def run_task_try(self):
        module = self.get_module()
        if module:
            if hasattr(module,'run_task_try'):
                return await module.run_task_try(self)
            raise NotImplementedError("""%s run_task_try(task) NOT IMPLEMENTED

edit %s.py:
async def run_task_try(task):
    # your core
    """ % (module.__name__,module.__name__.replace('.','/')))
        raise NotImplementedError("""%s run_task_try() NOT IMPLEMENTED

class %s:
    async def run_task_try(self):
        # your core
""" % (self.__class__.__name__,self.__class__.__name__))

    async def run_task_except(self,e):
        try:
            logging.error(e)
            await self.error(e)
        finally:
            # postgres closed connection
            if 'server closed the connection unexpectedly' in str(e).lower():
                sys.exit(0) # restart worker. use docker `restart: always`

    async def run_task_finally(self):
        pass

    async def delete_task(self):
        await sync_to_async(type(self).objects.filter(id=self.id).delete)()

    async def update_task(self, **kwargs):
        await sync_to_async(type(self).objects.filter(id=self.id).update)(**kwargs)

    async def debug(self, msg):
        self.config, created = await sync_to_async(Config.objects.get_or_create)(
                db_table=self._meta.db_table
            )
        if self.config.is_debug or getattr(self,'is_debug',None):
            await sync_to_async(Debug.objects.create)(
                db_table=self._meta.db_table,
                task_id=str(self.id),
                msg=msg,
                created_at=datetime.now()
            )

    async def error(self,e):
        await sync_to_async(Error(
            db_table=self._meta.db_table,
            task_id=str(self.id),
            exc_type='.'.join(filter(None,[type(e).__module__,type(e).__name__])),
            exc_value=str(e),
            exc_traceback=''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
        ).save)()

    @classmethod
    def get_queryset(model):
        return model.objects.filter(is_enqueued=False).order_by('id')

    @classmethod
    async def put_tasks(model,q):
        if model._meta.db_table not in CONFIGS:
            CONFIGS[model._meta.db_table], created = await sync_to_async(Config.objects.get_or_create)(
                db_table=model._meta.db_table
            )
        config = CONFIGS[model._meta.db_table]
        if config.is_disabled:
            return
        enqueued_count = await sync_to_async(model.objects.filter(is_enqueued=True).count)()
        free_count = config.enqueue_limit - enqueued_count
        if free_count:
            ids = []
            qs = model.get_queryset()
            for task in await sync_to_async(list)(qs[0:free_count]):
                q.put_nowait(task)
                ids.append(task.id)
            if ids:
                await model.update_enqueued_tasks(ids)
            return len(ids)

    @classmethod
    async def update_enqueued_tasks(model,ids):
        kwargs = {'enqueued_at':datetime.now()} if hasattr(model,'enqueued_at') else {}
        await sync_to_async(model.objects.filter(id__in=ids).update)(**kwargs)


"""models.py
from django_asyncio_task_queue.models import AbstractTask

class BaseTask(AbstractTask):
    priority = models.IntegerField(default=0, null=False)

    is_pending = models.BooleanField(default=True,verbose_name='pending')
    is_enqueued = models.BooleanField(default=False,verbose_name='enqueued')
    is_completed = models.BooleanField(default=False,verbose_name='completed')
    is_disabled = models.BooleanField(default=False,verbose_name='disabled')

    created_at = models.DateTimeField(auto_now_add=True)
    enqueued_at = models.DateTimeField(null=True)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    disabled_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        abstract = True

    async def get_module_name(self):
        return 'tasks.%s' % self._meta.db_table

    @classmethod
    def get_queryset(model):
        return model.objects.filter(
            is_completed=False, is_enqueued=False, is_disabled=False
        ).order_by('-priority', 'id')

    async def update_enqueued_tasks(self,ids):
        await sync_to_async(model.objects.filter(id__in=ids).update)(
            enqueued_at=datetime.now(),is_enqueued=True, is_pending=False
        )

    async def complete_task(self, **kwargs):
        completed_at = datetime.now()
        duration = str(completed_at - self.started_at)[0:7] if self.started_at else None
        await self.debug(''.join(['COMPLETED',': %s' % duration if duration else '']))
        kwargs.update(
            is_completed=True,
            is_disabled=False,
            is_enqueued=False,
            is_pending=False,
            completed_at=completed_at,
            disabled_at=None,
            started_at=self.started_at
        )
        await self.update_task(**kwargs)

    async def delete_task(self,msg=None):
        await sync_to_async(type(self).objects.filter(id=self.id).delete)()
        await self.debug(''.join(['DELETED',': %s' % msg if msg else '']))

    async def disable_task(self,msg=None):
        kwargs = dict(
            is_completed=False,
            is_disabled=True,
            is_enqueued=False,
            is_pending=False,
            completed_at=None,
            disabled_at=datetime.now(),
            enqueued_at=None,
            started_at=None
        )
        await self.update_task(**kwargs)
        await self.debug(''.join(['DISABLED',': %s' % msg if msg else '']))


class YourTask(BaseTask):
    # extra fields

    class Meta:
        db_table = 'tasks_name'
"""

"""tasks/db_table.py

async def run_task_try(task):
    # your task code
    await task.complete_task()
"""

