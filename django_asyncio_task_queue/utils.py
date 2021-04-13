import asyncio
from datetime import datetime


from asgiref.sync import sync_to_async
import django
from django.conf import settings

from .models import AbstractTask

STARTED_AT = datetime.now()
RESTART_INTERVAL = getattr(settings,'ASYNCIO_TASK_QUEUE_RESTART_INTERVAL',None)
SLEEP_INTERVAL = float(getattr(settings,'ASYNCIO_TASK_QUEUE_SLEEP_INTERVAL',1))


def get_models():
    return list(filter(
        lambda m:issubclass(m,AbstractTask) and not m._meta.abstract,
        django.apps.apps.get_models()
    ))


def unqueue_tasks():
    for model in get_models():
        qs = model.objects.filter(is_enqueued=True)
        if qs.count():
            qs.update(is_enqueued=False)


async def put_tasks(q):
    config_list = await sync_to_async(list)(Config.objects.all())
    configs = {c.db_table: c for c in config_list}
    for model in await get_models():
        db_table=model._meta.db_table
        enqueued_count = await sync_to_async(model.objects.filter(is_enqueued=True).count)()
        config = configs.get(db_table,None)
        if not config:
            config, created = await sync_to_async(model.objects.get_or_create)(db_table=db_table)
        free_count = (config.enqueue_limit or 42) - enqueued_count
        if config.is_disabled or free_count <= 0:
            continue
        qs = model.get_queryset()
        task_list = await sync_to_async(list)(qs[0:free_count].all())
        if task_list:
            for task in task_list:
                task.is_logged = config.is_logged
                q.put_nowait(task)
            ids = list(map(lambda t:t.id,task_list))
            await sync_to_async(model.objects.filter(id__in=ids).update)(
                is_enqueued=True, enqueued_at=datetime.now()
            )


async def put_tasks_loop(q):
    while True:
        await asyncio.sleep(SLEEP_INTERVAL)
        await put_tasks(q)


async def restart_loop(q):
    while True:
        if RESTART_INTERVAL and STARTED_AT + timedelta(seconds=RESTART_INTERVAL) < datetime.now():
            sys.exit(0)
        await asyncio.sleep(10)


async def worker_loop(q):
    while True:
        try:
            task = await q.get()
            await task.run_task()
            q.task_done()
        except asyncio.QueueEmpty:
            await asyncio.sleep(1)
