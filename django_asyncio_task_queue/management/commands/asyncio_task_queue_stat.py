from django.core.management.base import BaseCommand

from django_asyncio_task_queue.models import Exc, Log, Stat
from django_asyncio_task_queue.utils import get_models


class Command(BaseCommand):

    def handle(self, *args, **options):
        for model in await get_models():
            completed_tasks_count=model.objects.filter(is_completed=True).count()
            disabled_tasks_count=model.objects.filter(is_disabled=True).count()
            enqueued_tasks_count=model.objects.filter(is_enqueued=True).count()
            pending_tasks_count=model.objects.filter(is_completed=False, is_enqueued=False, is_disabled=False).count()
            restarted_tasks_count=model.objects.filter( is_restarted=True).count()
            defaults = dict(
                tasks_count=count,
                completed_tasks_count=completed_tasks_count,
                disabled_tasks_count=disabled_tasks_count,
                enqueued_tasks_count=enqueued_tasks_count,
                pending_tasks_count=pending_tasks_count,
                restarted_tasks_count=restarted_tasks_count,
                exc_count=Exc.objects.filter(db_table=model._meta.db_table).count(),
                logs_count=Log.objects.filter(db_table=model._meta.db_table).count(),
                updated_at=datetime.now()
            )
            Stat.objects.update_or_create(defaults,db_table=model._meta.db_table)
