from django.core.management.base import BaseCommand

from datetime import datetime

from django_asyncio_task_queue.models import Stat
from django_asyncio_task_queue.utils import get_models

class Command(BaseCommand):

    def handle(self, *args, **options):
        Stat.objects.exclude(
            db_table__in=list(map(lambda m:m._meta.db_table,get_models()))
        ).delete()
        db_tables = list(Stat.objects.values_list('db_table',flat=True))
        for model in get_models():
            kwargs = dict(
                tasks_count = model.objects.all().count(),
                completed_tasks_count = model.objects.filter(is_completed=True).count(),
                disabled_tasks_count = model.objects.filter(is_disabled=True).count(),
                enqueued_tasks_count = model.objects.filter(is_enqueued=True).count(),
                failed_tasks_count = model.objects.filter(is_failed=True).count(),
                pending_tasks_count = model.objects.filter(is_pending=False).count(),
                updated_at=datetime.now()
            )
            if model._meta.db_table in db_tables:
                Stat.objects.filter(db_table=model._meta.db_table).update(**kwargs)
            else:
                Stat.objects.get_or_create(kwargs,db_table=model._meta.db_table)



