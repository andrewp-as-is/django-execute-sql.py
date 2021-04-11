

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
        try:
            put_items(q)
            await asyncio.sleep(10)
        except Exception as e:
            try:
                logging.error(e, exc_info=True)
            finally:
                await asyncio.sleep(10)
                sys.exit(1)
