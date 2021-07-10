from django.apps import apps
from django.core.management.base import BaseCommand

from ...models import Stat
from ...utils import refresh_stat

class Command(BaseCommand):
    def handle(self, *args, **options):
        for stat in Stat.objects.all():
            model = apps.get_model(*stat.label.split('.'))
            refresh_stat(model)
