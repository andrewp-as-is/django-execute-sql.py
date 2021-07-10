from datetime import datetime
import importlib
import inspect
import logging
import os
import sys
import traceback

from asgiref.sync import sync_to_async
from django.db import models

from .error import Error
from .log import Log
from .model import Model

class AbstractBaseTask(models.Model):
    id = models.IntegerField(primary_key=True)

    class Meta:
        abstract = True

    @classmethod
    def init_model(model):
        pass

    def get_db_table(self):
        return self._meta.db_table

    async def run_task(self):
        raise NotImplementedError

    async def push(self,q):
        raise NotImplementedError

    async def delete_task(self):
        await sync_to_async(type(self).objects.filter(id=self.id).delete)()

    async def update_task(self, **kwargs):
        await sync_to_async(type(self).objects.filter(id=self.id).update)(**kwargs)

    async def log(self, msg):
        await sync_to_async(Log.objects.create)(
            app_label = self._meta.app_label,
            label=self._meta.label,
            task_id=str(self.id),
            msg=msg,
            created_at=datetime.now()
        )

    async def error(self,e):
        logging.error(e)
        await sync_to_async(Error(
            app_label = self._meta.app_label,
            label=self._meta.label,
            task_id=str(self.id),
            exc_type='.'.join(filter(None,[type(e).__module__,type(e).__name__])),
            exc_value=str(e),
            exc_traceback=''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
        ).save)()

class AbstractTask(AbstractBaseTask):
    priority = models.IntegerField(default=0,verbose_name='priority')

    is_enabled = models.BooleanField(default=True,verbose_name='enabled')
    is_waiting = models.BooleanField(default=True,verbose_name='waiting')
    is_pushed = models.BooleanField(default=False,verbose_name='pushed')

    created_at = models.DateTimeField(auto_now_add=True,verbose_name='created')
    pushed_at = models.DateTimeField(null=True,blank=True,verbose_name='pushed')
    started_at = models.DateTimeField(null=True,blank=True,verbose_name='started')
    finished_at = models.DateTimeField(null=True,blank=True,verbose_name='finished')
    updated_at = models.DateTimeField(null=True,blank=True,verbose_name='updated')

    class Meta:
        abstract = True

    @classmethod
    def init_model(model):
        m, created = Model.objects.get_or_create(label=model._meta.label)
        model.push_limit = m.push_limit
        model.objects.filter(is_pushed=True).update(is_pushed=False)

    @classmethod
    async def get_pushed_count(model):
        return await sync_to_async(model.objects.filter(is_pushed=True).count)()

    @classmethod
    def get_push_limit(model):
        return model.push_limit

    @classmethod
    async def push(model,q):
        push_limit = model.get_push_limit()
        if inspect.iscoroutinefunction(model.get_pushed_count):
            pushed_count = await model.get_pushed_count()
        else:
            pushed_count = model.get_pushed_count()
        free_count = push_limit - pushed_count
        if free_count:
            task_list = await sync_to_async(list)(model.get_queryset()[0:free_count])
            for task in task_list:
                q.put_nowait(task)
            if task_list:
                await sync_to_async(model.objects.filter(
                    id__in=map(lambda t:t.id,task_list)
                ).update)(is_pushed=True,pushed_at=datetime.now())
                return len(task_list)

    @classmethod
    def get_queryset(model):
        return model.objects.filter(is_waiting=True,is_pushed=False).order_by('-priority')

    async def update_task(self, **kwargs):
        kwargs['updated_at'] = datetime.now()
        await sync_to_async(type(self).objects.filter(id=self.id).update)(**kwargs)

    async def finish_task(self, **kwargs):
        kwargs.update(
            is_waiting=False,
            is_pushed=False,
            started_at=kwargs.get('started_at',self.started_at),
            finished_at=datetime.now()
        )
        await self.update_task(**kwargs)

    async def disable_task(self, **kwargs):
        kwargs.update(
            is_enabled=False,
            is_waiting=False,
            is_pushed=False,
        )
        await sync_to_async(type(self).objects.filter(id=self.id).update)(**kwargs)
