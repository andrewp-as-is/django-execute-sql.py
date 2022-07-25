from datetime import datetime
import logging
import os
import sys
import traceback

from django.db import connection
from django.core.management.base import BaseCommand

from ...models import Error

def execute_sql_file(path,ignore_errors):
    cursor = connection.cursor()
    try:
        # print(path)
        sql = open(path).read()
        cursor.execute(sql)
    except Exception as e:
        logging.error(e)
        print(type(e))
        Error(
            sql=open(path).read(),
            exc_type=type(e),
            exc_value=str(e),
            exc_traceback=traceback.format_exc(),
            created_at = datetime.now()
        ).save()
        if not ignore_errors:
            raise e


class Command(BaseCommand):
    def add_arguments(self , parser):
        parser.add_argument('-i','--ignore-errors',default=False, action='store_true')
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        path = options.get('path')
        if not os.path.exists(path):
            sys.exit('%s NOT EXISTS' % path)
        if os.path.isfile(path):
            return execute_sql_file(path)
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for f in filter(lambda f:os.path.splitext(f)[1]=='.sql',files):
                    execute_sql_file(os.path.join(root,f),options.get('ignore_errors',False))
        sys.exit('%s NOT A FILENAME/DIRECTORY' % path)
