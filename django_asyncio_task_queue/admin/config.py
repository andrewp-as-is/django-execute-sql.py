from django.contrib import admin
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.html import format_html
from django.urls import include, path

from django_asyncio_task_queue.models import Config

class ConfigAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Config._meta.get_fields()]+['account_actions']
    search_fields = ['db_table', ]

    def has_delete_permission(self, request, obj=None):
       return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'run_command/<slug:name>',
                self.admin_site.admin_view(self.run_command),
                name='run_command',
            )
        ]
        return custom_urls + urls

    def account_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Deposit</a> ',
            reverse('admin:run_command', args=['name']),
        )
    account_actions.short_description = 'Account Actions'
    account_actions.allow_tags = True

    def run_command(self, request, slug):
        return redirect('/test')

admin.site.register(Config, ConfigAdmin)
