from datetime import datetime

from django.contrib import admin
from django.utils.timesince import timesince

from django_asyncio_task_queue.models import AbstractTask

# [f.name for f in AbstractTask._meta.get_fields()]
LIST_DISPLAY = [
    'priority',
    'is_debug',
    'is_pending',
    'is_enqueued',
    'is_completed',
    'is_failed',
    'is_disabled',

    # 'enqueued_at_format',
    # 'enqueued_at_timesince',
    'get_enqueued_at',
    'get_started_at',
    'get_completed_at',
    #'completed_at_timesince',
    'duration',
    # 'timesince'
]

def get_datetime(value):
    if not value:
        return '-'
    if value.today()==datetime.now().today():
        return value.strftime("%H:%M:%S")
    return value.strftime("%Y-%m-%d")

class TaskAdmin(admin.ModelAdmin):
    fields = ['id']+[f.name for f in AbstractTask._meta.get_fields()]
    list_display = ['id']+LIST_DISPLAY
    list_filter = [f.name for f in AbstractTask._meta.get_fields() if 'is_' in f.name]
    readonly_fields = [
        'id',

        'created_at',
        'enqueued_at',
        'started_at',
        'completed_at',

        'is_enqueued',
        'is_failed',
    ]
    # search_fields = ['id', ]

    def has_delete_permission(self, request, obj=None):
       return False

    def enqueued_at_timesince(self, task):
        if not task.enqueued_at:
            return '-'
        return '%s ago' % timesince(task.enqueued_at).split(',')[0]
    enqueued_at_timesince.short_description = ''

    def get_enqueued_at(self, task):
        return get_datetime(task.enqueued_at)
    get_enqueued_at.short_description = 'enqueued_at'

    def get_started_at(self, task):
        return get_datetime(task.started_at)
    get_started_at.short_description = 'started_at'

    def get_completed_at(self, task):
        return get_datetime(task.completed_at)
    get_completed_at.short_description = 'completed_at'

    def completed_at_timesince(self, task):
        if not task.completed_at:
            return '-'
        return '%s ago' % timesince(task.completed_at).split(',')[0]
    completed_at_timesince.short_description = ''

        #return task.enqueued_at.strftime("%d %b %Y %H:%M:%S")
    #enqueued_at_timesince.admin_order_field = 'enqueued_at'
    #enqueued_at_timesince.short_description = 'enqueued at'


   # def enqueued_at_timesince(self, task):
   #     if not task.completed_at or not task.completed_at:
    #        return ''
    #    return timesince(task.completed_at-task.started_at).split(',')[0]+' ago'

        #return task.enqueued_at.strftime("%d %b %Y %H:%M:%S")
    #enqueued_at_timesince.admin_order_field = 'enqueued_at'
    #enqueued_at_timesince.short_description = 'enqueued at'

    def duration(self, task):
        if task.started_at and task.completed_at:
            s = str(task.completed_at - task.started_at)
            return s.split('.')[0] + '.' + s.split('.')[1][0:6] if '.' in s else s
    duration.short_description = 'duration'
