from datetime import datetime, timedelta
import sys

import asyncio
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.tasks.utils import cancel_enqueued_tasks

from .utils import main_loop, workers_loop
from django_asyncio_tasks.utils import put_items_loop


class TasksCommand(BaseCommand):
    coroutines = None
    q = None
    workers = None

    def add_arguments(self , parser):
        parser.add_argument('workers_count', type=int)

    def handle(self, *args, **options):
        register_workers
        workers_count = int(options.get('workers_count'))
        cancel_enqueued_tasks()
        self.q = asyncio.Queue()
        ioloop = asyncio.get_event_loop()
        tasks = [ioloop.create_task(self.put_items_loop()),]
        for _ in range(1, workers_count + 1):
            tasks.append(ioloop.create_task(workers_loop(self.q)))
        ioloop.run_until_complete(asyncio.wait(tasks))
        ioloop.close()

    def getcoroutines(self):
        coroutines = []
        for _ in range(1, workers_count + 1):
            coroutines.append(ioloop.create_task(workers_loop(self.q)))

    async def put_items_loop(self,q):
        await put_items_loop(q)
