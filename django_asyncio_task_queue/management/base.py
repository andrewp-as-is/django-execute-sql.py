import asyncio
from datetime import datetime
import logging
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from django_asyncio_task_queue.utils import get_models

STARTED_AT = datetime.now()
SLEEP_SECONDS = getattr(settings,'ASYNCIO_TASK_QUEUE_SLEEP',1)
RESTART_SECONDS = getattr(settings,'ASYNCIO_TASK_QUEUE_RESTART_SECONDS',None)
RESTART_COUNT = getattr(settings,'ASYNCIO_TASK_QUEUE_RESTART_COUNT',None)


class WorkerCommand(BaseCommand):
    args = None
    options = None
    q = None
    models = None
    sleep_seconds = None
    restart_seconds = None

    def add_arguments(self , parser):
        parser.add_argument('workers_count', type=int)

    def handle(self, *args, **options):
        self.args = args
        self.options = options
        self.q = asyncio.Queue()
        for model in self.get_models():
            model.objects.filter(is_enqueued=True).update(is_enqueued=False,is_pending=True)
        ioloop = asyncio.get_event_loop()
        ioloop.run_until_complete(asyncio.wait(self.get_aws(self.q)))
        ioloop.close()

    def get_aws(self,q):
        ioloop = asyncio.get_event_loop()
        aws = [
            ioloop.create_task(self.put_tasks_loop(q)),
            ioloop.create_task(self.restart_loop()),
        ]
        for _ in range(1, self.get_workers_count() + 1):
            aws.append(ioloop.create_task(self.worker_loop(q)))
        return aws

    def get_sleep_seconds(self):
        if self.sleep_seconds:
            return float(self.sleep_seconds)
        return float(SLEEP_SECONDS)

    def get_restart_seconds(self):
        for restart_seconds in [self.restart_seconds,RESTART_SECONDS]:
            if restart_seconds:
                return float(restart_seconds)

    def get_workers_count(self):
        return self.options.get('workers_count')

    async def run_task(self,task):
        await task.run_task()

    def get_models(self):
        return self.models if self.models else get_models()

    async def put_tasks(self,q):
        count = 0
        for model in self.get_models():
            count+=(await model.put_tasks(q) or 0)
        return count

    async def put_tasks_loop(self,q):
        count = 0
        try:
            while True:
                await asyncio.sleep(self.get_sleep_seconds())
                count+=(await self.put_tasks(q) or 0)
                if count and RESTART_COUNT and count>=RESTART_COUNT:
                    sys.exit(0)
        except Exception as e:
            logging.error(e)
            sys.exit(0)

    async def restart_loop(self):
        while True:
            restart_seconds = self.get_restart_seconds()
            if restart_seconds and STARTED_AT + timedelta(seconds=restart_seconds) < datetime.now():
                sys.exit(0)
            await asyncio.sleep(10)

    async def worker_loop(self,q):
        try:
            while True:
                try:
                    task = await q.get()
                    task.started_at = datetime.now()
                    await self.run_task(task)
                    q.task_done()
                    await asyncio.sleep(0.01)
                except asyncio.QueueEmpty:
                    await asyncio.sleep(1)
        except Exception as e:
            logging.error(e)
            sys.exit(0)
