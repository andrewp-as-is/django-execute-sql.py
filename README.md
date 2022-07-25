[![](https://img.shields.io/badge/released-2022.7.25-green.svg?longCache=True)](https://pypi.org/project/django-execute-sql/)
[![](https://img.shields.io/badge/license-Unlicense-blue.svg?longCache=True)](https://unlicense.org/)

### Installation
```bash
$ pip install django-execute-sql
```

#### `settings.py`
```python
INSTALLED_APPS+=['django_execute_sql']
```
#### `migrate`
```bash
$ python manage.py migrate
```

### Features
+  error tracking
+  admin interface

### Examples
```bash
$ python manage.py execute_sql path/to/file.sql
$ python manage.py execute_sql path/to/folder # *.sql files
```

`-i/--ignore-errors`
```bash
$ python manage.py execute_sql -i path/to/folder
$ python manage.py execute_sql --ignore-errors path/to/folder
```

