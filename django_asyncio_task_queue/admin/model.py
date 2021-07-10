from django.apps import apps
from django.contrib import admin

from ..models import AbstractBaseTask, Model

def get_models():
    return list(filter(
        lambda m:issubclass(m,AbstractBaseTask) and not m._meta.abstract,
        apps.get_models()
    ))

class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','app_label','label','db_table','is_enabled','push_limit',]
    list_filter = ['app_label','is_enabled',]

    def db_table(self,obj):
        try:
            model = apps.get_model(*obj.label.split('.'))
            return model._meta.db_table
        except Exception as e:
            pass

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        model_list = list(Model.objects.all())
        for model in get_models():
            defaults = dict(app_label=model._meta.app_label)
            obj = next(filter(lambda model:model.label==model._meta.label,model_list),None)
            if not obj:
                obj, created = Model.objects.get_or_create(defaults,label=model._meta.label)
            for k,v in defaults.items():
                if getattr(obj,k)!=v:
                    Model.objects.filter(pk=obj.pk).update(**{k:v})
        return qs

    def get_search_fields(self,request):
        return [f.name for f in self.model._meta.get_fields()]

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(Model, ModelAdmin)
