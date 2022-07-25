from datetime import datetime
import traceback

from django.contrib import admin
from django.db import connection
from django.shortcuts import redirect
from django.template.defaultfilters import linebreaksbr
from django.urls import include, path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince


from ..models import Error, Sql

APP_LABEL = Error._meta.app_label

class SqlAdmin(admin.ModelAdmin):
    list_display = ['id','name','execute_btn','success','updated_at','updated_at_timesince']
    list_filter = ['name','success',]
    list_search = ['name','sql',]
    readonly_fields = ['success','updated_at']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'django_execute_sql/<int:pk>',
                self.admin_site.admin_view(self.execute_sql),
                name='django_execute_sql',
            )
        ]
        return custom_urls + urls

    def updated_at_timesince(self, obj):
        if obj.updated_at:
            return timesince(obj.updated_at).split(',')[0]+' ago'
    updated_at_timesince.short_description = ''

    def execute_btn(self, obj):
        return format_html(
            '<a class="button" href="{}">EXECUTE</a> ',
            reverse('admin:django_execute_sql', args=[obj.pk]),
        )
    execute_btn.short_description = ''
    execute_btn.allow_tags = True

    def execute_sql(self, request, pk):
        cursor = connection.cursor()
        obj = Sql.objects.get(pk=pk)
        try:
            cursor.execute(obj.sql)
            Sql.objects.filter(pk=pk).update(success=True,updated_at=datetime.now())
            url = reverse('admin:{}_{}_changelist'.format(Sql._meta.app_label, Sql._meta.model_name))
        except Exception as e:
            Sql.objects.filter(pk=pk).update(success=False,updated_at=datetime.now())
            error = Error.objects.create(
                sql=obj.sql,
                exc_type=type(e),
                exc_value=str(e),
                exc_traceback=traceback.format_exc(),
                created_at = datetime.now()
            )
            url = reverse('admin:{}_{}_change'.format(Error._meta.app_label, Error._meta.model_name), args=(error.pk,))
        return redirect(url)


admin.site.register(Sql, SqlAdmin)
