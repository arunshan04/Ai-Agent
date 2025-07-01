from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Create the host_packages table (raw SQL, not a Django model)'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS host_packages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    host_id INTEGER NOT NULL,
                    package_name TEXT NOT NULL,
                    installed_date TEXT,
                    FOREIGN KEY(host_id) REFERENCES cveapp_host(id)
                );
            ''')
        self.stdout.write(self.style.SUCCESS('host_packages table created or already exists.'))
