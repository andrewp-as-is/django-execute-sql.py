import django

from .models import AbstractTask


def get_models():
    return list(filter(
        lambda m:issubclass(m,AbstractTask) and not m._meta.abstract,
        django.apps.apps.get_models()
    ))



@sync_to_async
def update_tasks(model, ids):
    enqueued_at = datetime.now()
    model.objects.filter(id__in=ids).update(
        is_enqueued=True, enqueued_at=enqueued_at
    )

async def put_tasks(q,count):
    for model in get_models():
        model = task_class.model
        db_table = model._meta.db_table
        enqueued_count = await sync_to_async(model.objects.filter(
            is_enqueued=True).count)()
        enqueued_limit = 10
        if model._meta.db_table in configs:
            config = configs[db_table]
            if config.is_disabled:
                continue
            enqueued_limit = config.enqueued_limit or 10
        count = enqueued_limit - enqueued_count
        if count <= 0:
            continue
        qs = model.objects.filter(
            is_completed=False, is_enqueued=False, is_disabled=False
        ).order_by('-priority', 'activated_at')
        task_list = await sync_to_async(list)(qs[0:count].all())
        if task_list:
            for task in task_list:
                q.put_nowait(task)
            await sync_to_async(model.objects.filter(
                id__in=list(map(lambda t:t.id,task_list))
            ).update)(
                is_enqueued=True, enqueued_at=datetime.now()
            )

