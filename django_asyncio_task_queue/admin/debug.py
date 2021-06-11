from django.contrib import admin
from django_asyncio_task_queue.models import Debug

from .utils import set_verbose_name_plural

class DebugAdmin(admin.ModelAdmin):

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

    def has_delete_permission(self, request, obj=None):
       return False

admin.site.register(Debug, DebugAdmin)


