from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'List all database tables including Django default ones'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            if connection.vendor == 'postgresql':
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            elif connection.vendor == 'mysql':
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()")
            elif connection.vendor == 'sqlite':
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            else:
                self.stdout.write(self.style.ERROR('Unsupported database backend'))
                return

            tables = cursor.fetchall()
            self.stdout.write(self.style.SUCCESS('List of all tables:'))
            for table in tables:
                self.stdout.write(f"- {table[0]}")