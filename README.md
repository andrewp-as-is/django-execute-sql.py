[![](https://img.shields.io/badge/released-2021.8.20-green.svg?longCache=True)](https://pypi.org/project/django-asyncio-task-queue/)
[![](https://img.shields.io/badge/license-Unlicense-blue.svg?longCache=True)](https://unlicense.org/)

### Installation
```bash
$ pip install django-asyncio-task-queue
```

### Pros
+   base task models
+   error handling
+   log messages
+   management commands
+   admin interface

#### `settings.py`
```python
INSTALLED_APPS+=['django_asyncio_task_queue']

# optional:
ASYNCIO_TASK_QUEUE_SLEEP=0.1
ASYNCIO_TASK_QUEUE_MODELS=['my_app.Task1','my_app.Task2']
```
#### `migrate`
```bash
$ python manage.py migrate
```

### Examples
`models.py`
```python
from django_asyncio_task_queue.models import AbstractTask

class Task1(AbstractTask):
    custom_field1 = models.TextField()

    async def run_task(self):
        try:
            await task.log('msg')
            await task.finish_task()
        except Exception as e:
            await self.disable_task()
            await self.error(e)
```

`admin.py`
```python
from django.apps import apps
from django.contrib import admin

from django_asyncio_task_queue.admin import TaskAdmin
from django_asyncio_task_queue.models import AbstractTask

models = list(filter(
    lambda m:issubclass(m,AbstractTask) and not m._meta.abstract,
    apps.get_models()
))
for model in models:
    modelAdmin = type('%sAdmin' % model.__name__, (TaskAdmin,), {})
    admin.site.register(model, modelAdmin)
```

management commands
```bash
$ export DJANGO_ASYNCIO_TASK_QUEUE_MODELS='app.Model1,app.Model2' # optional. custom models
$ python manage.py asyncio_task_queue_worker 42 # 42 workers
```

```bash
$ python manage.py asyncio_task_queue_stat # collect stat for AbstractTask subclasses
```

