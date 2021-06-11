# Generated by Django 3.1.7 on 2021-05-03 02:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('db_table', models.TextField(primary_key=True, serialize=False)),
                ('enqueue_limit', models.IntegerField(default=42)),
                ('is_debug', models.BooleanField(default=False)),
                ('is_disabled', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Config',
                'db_table': 'asyncio_task_queue_config',
                'ordering': ('db_table',),
            },
        ),
        migrations.CreateModel(
            name='Debug',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('db_table', models.TextField()),
                ('task_id', models.TextField()),
                ('msg', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Debug',
                'db_table': 'asyncio_task_queue_debug',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Error',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('db_table', models.TextField()),
                ('task_id', models.TextField()),
                ('exc_type', models.TextField()),
                ('exc_value', models.TextField()),
                ('exc_traceback', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Error',
                'db_table': 'asyncio_task_queue_error',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Stat',
            fields=[
                ('db_table', models.TextField(primary_key=True, serialize=False)),
                ('tasks_count', models.IntegerField(null=True, verbose_name='all')),
                ('pending_tasks_count', models.IntegerField(null=True, verbose_name='pending')),
                ('enqueued_tasks_count', models.IntegerField(null=True, verbose_name='enqueued')),
                ('completed_tasks_count', models.IntegerField(null=True, verbose_name='completed')),
                ('failed_tasks_count', models.IntegerField(null=True, verbose_name='failed')),
                ('disabled_tasks_count', models.IntegerField(null=True, verbose_name='disabled')),
                ('errors_count', models.IntegerField(null=True, verbose_name='errors')),
                ('debug_messages_count', models.IntegerField(null=True, verbose_name='debug')),
                ('updated_at', models.DateTimeField(null=True)),
            ],
            options={
                'verbose_name_plural': 'Stat',
                'db_table': 'asyncio_task_queue_stat',
                'ordering': ('db_table',),
            },
        ),
    ]
