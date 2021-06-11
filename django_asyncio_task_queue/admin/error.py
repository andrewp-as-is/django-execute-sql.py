from django.contrib import admin
from django.utils.timesince import timesince

from django_asyncio_task_queue.models import Error

from .utils import set_verbose_name_plural

class ErrorAdmin(admin.ModelAdmin):
    # change_list_template = 'change_list.html'
    list_display = [f.name for f in Error._meta.get_fields()]+['timesince']
    list_filter = ['db_table','exc_type']

    def delete_model(self, request, obj):
        obj.delete(using=self.using)
        set_verbose_name_plural()

    def delete_queryset(self, request, queryset):
        queryset.delete()
        set_verbose_name_plural()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        set_verbose_name_plural()
        return qs

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request, obj=None):
        return False

    def timesince(self, stat):
        if stat.created_at:
            return timesince(stat.created_at).split(',')[0]+' ago'
    timesince.short_description = ''

admin.site.register(Error, ErrorAdmin)

