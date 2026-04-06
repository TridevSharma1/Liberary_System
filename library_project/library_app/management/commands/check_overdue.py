from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from datetime import date, timedelta
from library_app.models import IssueBook, Notification

class Command(BaseCommand):
    help = 'Check for overdue books and create notifications'

    def handle(self, *args, **options):
        today = date.today()
        
        # Find overdue books
        overdue_issues = IssueBook.objects.filter(
            is_returned=False,
            due_date__lt=today
        )
        
        overdue_count = 0
        for issue in overdue_issues:
            # Check if notification already exists for this overdue book
            existing_notification = Notification.objects.filter(
                student=issue.student,
                issue_book=issue,
                notification_type='overdue'
            ).exists()
            
            if not existing_notification:
                days_overdue = issue.days_overdue()
                message = f'Book "{issue.book.title}" is overdue by {days_overdue} days. Please return it immediately.'
                
                Notification.objects.create(
                    student=issue.student,
                    issue_book=issue,
                    message=message,
                    notification_type='overdue'
                )
                
                # Send email notification
                try:
                    send_mail(
                        subject='Library Book Overdue Notice',
                        message=f'Dear {issue.student.name},\n\n{message}\n\nFine: ₹{days_overdue * 10} ({days_overdue} days @ ₹10/day)\n\nPlease return the book as soon as possible.\n\nLibrary Management System',
                        from_email=None,
                        recipient_list=[issue.student.email],
                        fail_silently=True,
                    )
                    self.stdout.write(f'Email sent to {issue.student.email} for overdue book "{issue.book.title}"')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Failed to send email to {issue.student.email}: {e}'))
                
                overdue_count += 1
        
        # Find books due soon (within 3 days)
        due_soon_issues = IssueBook.objects.filter(
            is_returned=False,
            due_date__gte=today,
            due_date__lte=today + timedelta(days=3)
        )
        
        due_soon_count = 0
        for issue in due_soon_issues:
            # Check if notification already exists for this due soon book
            existing_notification = Notification.objects.filter(
                student=issue.student,
                issue_book=issue,
                notification_type='due_soon'
            ).exists()
            
            if not existing_notification:
                days_until_due = (issue.due_date - today).days
                message = f'Book "{issue.book.title}" is due in {days_until_due} days. Please return it on time.'
                
                Notification.objects.create(
                    student=issue.student,
                    issue_book=issue,
                    message=message,
                    notification_type='due_soon'
                )
                
                # Send email notification
                try:
                    send_mail(
                        subject='Library Book Due Soon Reminder',
                        message=f'Dear {issue.student.name},\n\n{message}\n\nDue Date: {issue.due_date}\n\nPlease return the book by the due date to avoid fines.\n\nLibrary Management System',
                        from_email=None,
                        recipient_list=[issue.student.email],
                        fail_silently=True,
                    )
                    self.stdout.write(f'Email sent to {issue.student.email} for due soon book "{issue.book.title}"')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Failed to send email to {issue.student.email}: {e}'))
                
                due_soon_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {overdue_count} overdue notifications and {due_soon_count} due soon notifications'
            )
        )