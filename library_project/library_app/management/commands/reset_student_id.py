from django.core.management.base import BaseCommand
from django.db import connection
from library_app.models import Student
from django.contrib import messages

class Command(BaseCommand):
    help = 'Reset all student records and reset the ID counter to start from 1'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without prompting',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            confirm = input('⚠️  This will DELETE all students and reset ID counter. Type "yes" to confirm: ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.WARNING('Operation cancelled.'))
                return

        try:
            # Get the database vendor (sqlite, postgresql, mysql, etc.)
            db_vendor = connection.vendor
            
            # Delete all students
            count = Student.objects.count()
            Student.objects.all().delete()
            
            # Reset the auto-increment sequence
            if db_vendor == 'sqlite':
                # For SQLite, delete from sqlite_sequence
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM sqlite_sequence WHERE name='library_app_student'"
                    )
            elif db_vendor == 'postgresql':
                # For PostgreSQL
                with connection.cursor() as cursor:
                    cursor.execute(
                        "ALTER SEQUENCE library_app_student_id_seq RESTART WITH 1"
                    )
            elif db_vendor == 'mysql':
                # For MySQL
                with connection.cursor() as cursor:
                    cursor.execute("ALTER TABLE library_app_student AUTO_INCREMENT = 1")
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Successfully deleted {count} student(s) and reset ID counter to 1'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error: {str(e)}')
            )
