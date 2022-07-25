from setuptools import setup

setup(
    name='django-execute-sql',
    version='2022.7.25',
    packages=[
        'django_execute_sql',
        'django_execute_sql.admin',
        'django_execute_sql.management',
        'django_execute_sql.management.commands',
        'django_execute_sql.migrations',
        'django_execute_sql.models'
    ]
)
