from django.db import models
from django.contrib.auth.models import User

# Student Model
class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return self.user.username

# Book Model
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=20, unique=True)
    total_quantity = models.PositiveIntegerField(default=1)
    available_quantity = models.PositiveIntegerField(default=1)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.total_quantity < 0:
            raise ValidationError('Total quantity cannot be negative.')
        if self.available_quantity < 0:
            raise ValidationError('Available quantity cannot be negative.')
        if self.available_quantity > self.total_quantity:
            raise ValidationError('Available quantity cannot exceed total quantity.')
    
    def save(self, *args, **kwargs):
        self.clean()
        # Update available flag based on quantity
        self.available = self.available_quantity > 0
        super().save(*args, **kwargs)
    
    def issue_book(self):
        """Decrease available quantity when a book is issued."""
        if self.available_quantity > 0:
            self.available_quantity -= 1
            self.save()
            return True
        return False
    
    def return_book(self):
        """Increase available quantity when a book is returned."""
        if self.available_quantity < self.total_quantity:
            self.available_quantity += 1
            self.save()
            return True
        return False


# Issue Book Model
class IssueBook(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.student} - {self.book}"
    
    def save(self, *args, **kwargs):
        # Set default due date if not provided
        if not self.due_date:
            from datetime import date, timedelta
            self.due_date = date.today() + timedelta(days=7)
        super().save(*args, **kwargs)
    
    def calculate_fine(self):
        """Calculate fine if book is returned late (₹10 per day)"""
        from datetime import date
        if self.is_returned and self.return_date and self.due_date:
            if self.return_date > self.due_date:
                days_late = (self.return_date - self.due_date).days
                self.fine_amount = days_late * 10
                self.save()
                return self.fine_amount
        return 0
    
    def is_overdue(self):
        """Check if the book is overdue"""
        from datetime import date
        return not self.is_returned and self.due_date and date.today() > self.due_date
    
    def days_overdue(self):
        """Return number of days overdue"""
        from datetime import date
        if self.is_overdue():
            return (date.today() - self.due_date).days
        return 0


# Notification Model
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('overdue', 'Overdue Book'),
        ('due_soon', 'Due Soon'),
        ('returned', 'Book Returned'),
        ('issued', 'Book Issued'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    issue_book = models.ForeignKey(IssueBook, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.name} - {self.notification_type}"