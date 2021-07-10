import asyncio
from datetime import datetime, timedelta
import logging
import os
import sys

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.management.base import BaseCommand

from ..models import Model

RESTART_SECONDS = int(getattr(settings,'ASYNCIO_TASK_QUEUE_RESTART_SECONDS',None) or 0)
RESTART_COUNT = int(getattr(settings,'ASYNCIO_TASK_QUEUE_RESTART_COUNT',None) or 0)
SLEEP_SECONDS = getattr(settings,'ASYNCIO_TASK_QUEUE_SLEEP',1)
STARTED_AT = datetime.now()


class WorkerCommand(BaseCommand):
    args = None
    options = None
    q = None
    models = None
    restart_seconds = None
    sleep_seconds = None
    workers_count = None

    def add_arguments(self , parser):
        parser.add_argument('workers_count', type=int)

    def handle(self, *args, **options):
        self.args = args
        self.options = options
        self.q = asyncio.Queue()
        self.init()
        ioloop = asyncio.get_event_loop()
        ioloop.run_until_complete(asyncio.wait(self.get_aws(self.q)))
        ioloop.close()

    def init(self):
        if not self.models:
            self.models = []
            for m in Model.objects.filter(is_enabled=True):
                model = m.get_model()
                self.models.append(model)
        for model in self.models:
            if hasattr(model,'init_model'):
                model.init_model()

    def get_aws(self,q):
        ioloop = asyncio.get_event_loop()
        aws = [ioloop.create_task(self.push_loop(q))]
        for _ in range(1, self.get_workers_count() + 1):
            aws.append(ioloop.create_task(self.worker_loop(q)))
        return aws

    def get_restart_seconds(self):
        return self.restart_seconds if self.restart_seconds else RESTART_SECONDS

    def get_sleep_seconds(self):
        return self.sleep_seconds if self.sleep_seconds else SLEEP_SECONDS

    def get_workers_count(self):
        return self.workers_count if self.workers_count else self.options.get('workers_count')

    async def run_task(self,task):
        await task.run_task()

    async def push_loop(self,q):
        try:
            count = 0
            restart_seconds = self.get_restart_seconds()
            sleep_seconds = self.get_sleep_seconds()
            while True:
                await asyncio.sleep(sleep_seconds)
                for model in self.models:
                    result = await model.push(q)
                    if isinstance(result,int):
                        count+=result
                if RESTART_COUNT and count>=RESTART_COUNT:
                    sys.exit(0)
                if restart_seconds and STARTED_AT + timedelta(seconds=restart_seconds) < datetime.now():
                    sys.exit(0)
        except Exception as e:
            logging.error(e)
        finally:
            sys.exit(0)

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
        finally:
            sys.exit(0)
