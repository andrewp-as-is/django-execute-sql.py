# Generated by Django 3.1.7 on 2021-04-13 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('db_table', models.TextField(null=True)),
                ('is_logged', models.BooleanField(default=False)),
                ('is_disabled', models.BooleanField(default=False)),
                ('enqueue_limit', models.IntegerField(default=42)),
            ],
            options={
                'db_table': 'asyncio_task_queue_config',
            },
        ),
        migrations.CreateModel(
            name='Exc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('db_table', models.TextField()),
                ('task_id', models.IntegerField()),
                ('exc_type', models.TextField()),
                ('exc_value', models.TextField()),
                ('exc_traceback', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'asyncio_task_queue_exc',
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('db_table', models.TextField()),
                ('task_id', models.IntegerField()),
                ('msg', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'asyncio_task_queue_log',
            },
        ),
        migrations.CreateModel(
            name='Stat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('db_table', models.TextField(unique=True)),
                ('tasks_count', models.IntegerField()),
                ('completed_tasks_count', models.IntegerField()),
                ('pending_tasks_count', models.IntegerField()),
                ('enqueued_tasks_count', models.IntegerField()),
                ('restarted_tasks_count', models.IntegerField()),
                ('disabled_tasks_count', models.IntegerField()),
                ('exc_count', models.IntegerField()),
                ('logs_count', models.IntegerField()),
                ('updated_at', models.DateTimeField(null=True)),
            ],
            options={
                'db_table': 'asyncio_task_queue_stat',
            },
        ),
    ]
