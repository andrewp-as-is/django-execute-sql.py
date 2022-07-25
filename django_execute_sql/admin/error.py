from django.contrib import admin
from django.template.defaultfilters import linebreaksbr
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince

from ..models import Error

class ErrorAdmin(admin.ModelAdmin):
    list_display = ['id','exc_type','exc_value','sql_html','created_at','created_at_timesince']
    list_filter = ['exc_type',]
    list_search = ['sql','exc_type','exc_value','exc_traceback']

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request, obj=None):
        return False

    def has_edit_permission(self, request, obj=None):
        return False

    def sql_html(self,obj):
        return linebreaksbr(obj.sql.strip()) if obj.sql.strip() else None
    sql_html.short_description = 'sql'
    sql_html.allow_tags = True

    def exc_traceback_html(self,obj):
        return linebreaksbr(obj.exc_traceback) if obj.exc_traceback else None
    exc_traceback_html.short_description = 'traceback'
    exc_traceback_html.allow_tags = True

    def created_at_timesince(self, obj):
        if obj.created_at:
            return timesince(obj.created_at).split(',')[0]+' ago'
    created_at_timesince.short_description = ''

admin.site.register(Error, ErrorAdmin)
