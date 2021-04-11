import asyncio
from datetime import datetime, timedelta
import logging
import sys

import django.apps
from django.conf import settings

from .models import AbstractTask, Exc, Log


EXIT_INTERVAL = int(getattr(settings,'TASKS_EXIT_INTERVAL',None))
STARTED_AT = datetime.now()
WORKERS = []

IGNORED_FIELDS = [
    'is_completed',
    'is_disabled',
    'is_enqueued',
    'is_restarted',
    'disabled_at',
    'enqueued_at',
    'restarted_at',
    'updated_at'
]


def cancel_enqueued_tasks():
    for model in get_models():
        qs = model.objects.filter(is_enqueued=True)
        if qs.count():
            qs.update(is_enqueued=False)

def get_fields(model):
    fields = list(filter(lambda f: f.name not in IGNORED_FIELDS, model._meta.fields))
    return list(map(lambda f: f.name, fields))

def get_models():
    models = []
    for model in django.apps.apps.get_models():
        if issubclass(model,AbstractTask) and not model._meta.abstract:
            models.append(model)
    return models

def get_workers():
    return WORKERS

def register_worker(worker):
    WORKERS.append(worker)

def register_workers(workers):
    WORKERS+=workers

@sync_to_async
def save_exc(db_table, task_id):
    exc, exc_value, tb = sys.exc_info()
    Exc(
        db_table=db_table,
        task_id=task_id,
        exc_type=exc.__module__ + '.' + exc.__name__ if exc.__module__ else exc.__name__,
        exc_value=exc_value if exc_value else '',
        exc_traceback='\n'.join(format_tb(tb))
    ).save()

def put_items(q):
    config_list = await sync_to_async(list)(Config.objects.all())
    configs = {c.db_table: c for c in config_list}
    for task_class in TASK_CLASSES:
        model = task_class.model
        db_table=model._meta.db_table
        enqueued_count = await sync_to_async(model.objects.filter(is_enqueued=True).count)()
        config = configs.get(db_table,None)
        if not config:
            config, created = await sync_to_async(model.objects.get_or_create)(db_table=db_table)
        count = (config.limit or 10) - enqueued_count
        if config.is_disabled or count <= 0:
            continue
        qs = model.objects.filter(
            is_completed=False, is_enqueued=False, is_disabled=False
        ).only(*getfields(model)).order_by('-priority', 'activated_at')
        task_ids = []
        tasks = await sync_to_async(list)(qs[0:count].all())
        for task in tasks:
            task_ids.append(task.id)
            kwargs = {'is_logged':config.is_logged}
            for f in getfields(model):
                kwargs[f] = getattr(task, f)
            item = Item(task_class, kwargs)
            q.put_nowait(item)
        if task_ids:
            kwargs = dict(is_enqueued=True, enqueued_at=datetime.now())
            await sync_to_async(model.objects.filter(id__in=ids).update)(**kwargs)


async def put_items_loop(q):
    while True:
        if EXIT_INTERVAL and STARTED_AT + timedelta(seconds=EXIT_INTERVAL) < datetime.now():
            sys.exit(0)
        try:
            put_items(q)
            await asyncio.sleep(10)
        except Exception as e:
            try:
                logging.error(e, exc_info=True)
            finally:
                await asyncio.sleep(10)
                sys.exit(1)


async def run_worker(task):
    try:
        await task.log('INITING')
        await task.init()
        await task.log('INITED')
        task.started_at = datetime.now()
        if task.is_completed or task.is_deleted or task.is_disabled or task.is_restarted:
            return
        await task.log('RUNNING')
        await task.run()
        if not task.is_deleted and not task.is_disabled and not task.is_restarted:
            await task.complete()
    except (InterfaceError, OperationalError) as e:
        try:
            logging.error(e, exc_info=False)
        finally:
            await asyncio.sleep(60)
            sys.exit(0)  # restart
    except Exception as e:
        try:
            # do not spam stderr with exceptions
            # logging.error(e, exc_info=True)
            await task.log('%s: %s' % (type(e), str(e)))
            await save_exc(task.model._meta.db_table,task.id)
            await task.disable()
        finally:
            await asyncio.sleep(60)
    finally:
        await task.run_finally()


async def workers_loop(q):
    while True:
        try:
            item = await q.get()
            worker = item.worker(**item.kwargs)
            await run_worker(task)
            q.task_done()
            await asyncio.sleep(0.01)
        except asyncio.QueueEmpty:
            await asyncio.sleep(1)
        except Exception as e:
            await asyncio.sleep(10)
            sys.exit(1)
            # try:
            #    logging.error(e, exc_info=True)
            # finally:
            #    time.sleep(60)
