from setuptools import setup

setup(
    name='django-asyncio-task-queue',
    version='2021.6.11',
    install_requires=[
        'asgiref'
    ],
    packages=[
        'django_asyncio_task_queue',
        'django_asyncio_task_queue.admin',
        'django_asyncio_task_queue.management',
        'django_asyncio_task_queue.management.commands',
        'django_asyncio_task_queue.migrations',
        'django_asyncio_task_queue.models'
    ]
)
