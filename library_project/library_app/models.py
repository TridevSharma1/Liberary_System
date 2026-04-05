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
    return_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student} - {self.book}"