import asyncio
from django.core.management.base import BaseCommand

from django_asyncio_task_queue.utils import get_models, put_tasks_loop, restart_loop, worker_loop, unqueue_tasks


class WorkerCommand(BaseCommand):
    options = None
    workers_count = None
    q = None

    def add_arguments(self , parser):
        parser.add_argument('workers_count', type=int)

    def handle(self, *args, **options):
        self.options = options
        self.q = asyncio.Queue()
        self.unqueue_tasks()
        ioloop = asyncio.get_event_loop()
        ioloop.run_until_complete(asyncio.wait(self.get_awaitable_objects()))
        ioloop.close()

    def get_workers_count(self):
        return self.options.get('workers_count')

    def get_awaitable_objects(self):
        awaitable_objects = [
            ioloop.create_task(self.put_tasks_loop(self.q)),
            ioloop.create_task(self.restart_loop()),
        ]
        for _ in range(1, self.get_workers_count() + 1):
            awaitable_objects.append(ioloop.create_task(self.worker_loop(self.q)))
        return awaitable_objects

    async def put_tasks_loop(self,q):
        await put_tasks_loop(q)

    async def restart_loop(self):
        await restart_loop()

    async def worker_loop(self,q):
        await worker_loop(q)

    async def unqueue_tasks(self):
        await unqueue_tasks()

