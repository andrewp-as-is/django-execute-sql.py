from datetime import datetime, timedelta
import sys

import asyncio
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.tasks.utils import cancel_enqueued_tasks

from django_asyncio_tasks.utils import main_loop, worker_loop

class Item:

    def __init__(self, task_class, kwargs):
        self.task_class = task_class
        self.kwargs = kwargs

class Command(BaseCommand):
    def add_arguments(self , parser):
        parser.add_argument('workers', type=int)

    def handle(self, *args, **options):
        workers_count = int(options.get('workers'))
        cancel_enqueued_tasks()
        q = asyncio.Queue()
        ioloop = asyncio.get_event_loop()
        tasks = [ioloop.create_task(main_loop(q)),]
        for _ in range(1, workers_count + 1):
            tasks.append(ioloop.create_task(worker_loop(q)))
        ioloop.run_until_complete(asyncio.wait(tasks))
        ioloop.close()
