from datetime import datetime

from django.apps import apps

from .models import AbstractBaseTask, Error, Log, Stat


def refresh_stat(model):
    qs = model.objects.all()
    count = qs.count()
    disabled_count = qs.filter(is_enabled=False).count()
    enabled_count = count - disabled_count
    done_count = qs.filter(is_waiting=False).count()
    pushed_count = qs.filter(is_pushed=True).count()
    waiting_count = qs.filter(is_waiting=True).count()
    error_count = Error.objects.filter(label=model._meta.label).count()
    log_count = Log.objects.filter(label=model._meta.label).count()
    defaults = dict(
        app_label = model._meta.app_label,
        count = count,
        enabled_count = enabled_count,
        disabled_count = disabled_count,
        done_count = done_count,
        pushed_count = pushed_count,
        waiting_count = waiting_count,
        error_count = error_count,
        log_count = log_count,
        updated_at = datetime.now()
    )
    Stat.objects.update_or_create(defaults,label=model._meta.label)
