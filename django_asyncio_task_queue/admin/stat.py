from django.apps import apps
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.timesince import timesince

from ..models import AbstractTask, Stat
from ..utils import refresh_stat

def get_models():
    return list(filter(
        lambda m:issubclass(m,AbstractTask) and not m._meta.abstract,
        apps.get_models()
    ))

class StatAdmin(admin.ModelAdmin):
    list_display = ['id','app_label','label','db_table','count','enabled_count','disabled_count','waiting_count','pushed_count','logs','errors','refresh_button','updated_at','timesince',]
    list_filter = ['app_label',]

    def db_table(self,obj):
        try:
            model = apps.get_model(*obj.label.split('.'))
            return model._meta.db_table
        except Exception:
            pass

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        for model in get_models():
            defaults = dict(app_label=model._meta.app_label)
            Stat.objects.get_or_create(defaults,label=model._meta.label)
        return qs

    def get_search_fields(self,request):
        return [f.name for f in self.model._meta.get_fields()]

    def get_urls(self):
        return [
            path(
                'django_asyncio_task_queue_stat_refresh/<str:label>',
                self.admin_site.admin_view(self.refresh),
                name='django_asyncio_task_queue_stat_refresh',
            ),
        ] + super().get_urls()

    def has_add_permission(self, request, obj=None):
        return False

    def errors(self, stat):
        if stat.error_count is None:
            return
        return format_html(
            '<a href="{}">%s</a>' % stat.error_count,
            reverse('admin:django_asyncio_task_queue_error_changelist')+'?label='+stat.label,
        )
    errors.short_description = 'errors'
    errors.allow_tags = True

    def logs(self, stat):
        if stat.log_count is None:
            return
        return format_html(
            '<a href="{}">%s</a>' % stat.log_count,
            reverse('admin:django_asyncio_task_queue_log_changelist')+'?label='+stat.label,
        )
    logs.short_description = 'logs'
    logs.allow_tags = True

    def refresh_button(self, model):
        return format_html(
            '<a class="button" href="{}">Refresh</a>',
            reverse('admin:django_asyncio_task_queue_stat_refresh', args=[model.label]),
        )
    refresh_button.short_description = ''
    refresh_button.allow_tags = True

    def refresh(self, request, label):
        model = apps.get_model(*label.split('.'))
        refresh_stat(model)
        url = reverse('admin:django_asyncio_task_queue_stat_changelist')
        return redirect(url)

    def timesince(self,stat):
        if stat.updated_at:
            return timesince(stat.updated_at).split(',')[0]+' ago'
    timesince.short_description = 'updated'

admin.site.register(Stat, StatAdmin)
