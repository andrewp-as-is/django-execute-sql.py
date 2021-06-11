from django.contrib import admin
from django.urls import reverse
from django.utils.timesince import timesince
from django.utils.safestring import mark_safe

from django_asyncio_task_queue.models import Stat
from django_asyncio_task_queue.utils import get_models

def get_admin_url(db_table):
    for model in get_models():
        if model._meta.db_table==db_table:
            return (reverse('admin:index') or '/')+model._meta.app_label+'/'+model._meta.model_name.replace('_','')


class StatAdmin(admin.ModelAdmin):
    list_display = ['get_db_table','get_pending_tasks_count']+[field.name for field in Stat._meta.get_fields()]+['timesince']

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
       return False

    def get_db_table(self,stat):
        url = get_admin_url(stat.db_table)
        text = stat.db_table
        return mark_safe('<a href="%s">%s</a>' % (url,text))
    get_db_table.short_description = 'db_table'

    def get_pending_tasks_count(self,stat):
        url = get_admin_url(stat.db_table)+'/?is_pending__exact=1'
        text = stat.pending_tasks_count
        return mark_safe('<a href="%s">%s</a>' % (url,text))
    get_pending_tasks_count.short_description = 'pending'


    def get_errors_count(self,stat):
        url = get_admin_url(stat.db_table)+'/?is_pending__exact=1'
        text = stat.pending_tasks_count
        return mark_safe('<a href="%s">%s</a>' % (url,text))
    get_errors_count.short_description = 'pending'

    def timesince(self, stat):
        if stat.updated_at:
            return timesince(stat.updated_at).split(',')[0]+' ago'
    timesince.short_description = ''


admin.site.register(Stat, StatAdmin)

