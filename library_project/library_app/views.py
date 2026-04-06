from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Student, Book, IssueBook, Notification
from .forms import StudentForm, BookForm, IssueBookForm, StudentSearchForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import send_mail

def home(request):
    return render(request, 'home.html')


def add_student(request):
    form = StudentForm(request.POST or None)
    if form.is_valid():
        student = form.save()
        messages.success(request, f'✓ Student "{student.name}" has been added successfully!')
        return redirect('home')
    return render(request, 'add_student.html', {'form': form})


def add_book(request):
    form = BookForm(request.POST or None)
    if form.is_valid():
        book = form.save()
        messages.success(request, f'✓ Book "{book.title}" has been added successfully! (Quantity: {book.total_quantity})')
        return redirect('home')
    return render(request, 'add_book.html', {'form': form})


from datetime import date, timedelta

def issue_book(request):
    form = IssueBookForm(request.POST or None)

    if form.is_valid():
        issue = form.save(commit=False)

        # Check if book is available before saving
        if issue.book.available_quantity > 0:
            # Save the issue first
            issue.save()
            
            # Then decrease book quantity
            issue.book.issue_book()
            
            # Create notification
            Notification.objects.create(
                student=issue.student,
                issue_book=issue,
                message=f'Book "{issue.book.title}" has been issued successfully. Due date: {issue.due_date}',
                notification_type='issued'
            )
            
            # Send email notification
            try:
                send_mail(
                    subject='Library Book Issued Successfully',
                    message=f'Dear {issue.student.name},\n\nBook "{issue.book.title}" has been issued to you successfully.\n\nIssue Date: {issue.issue_date}\nDue Date: {issue.due_date}\n\nPlease return the book by the due date to avoid fines (₹10 per day late).\n\nLibrary Management System',
                    from_email=None,
                    recipient_list=[issue.student.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Failed to send email: {e}")
            
            messages.success(request, f'✓ Book "{issue.book.title}" has been issued to {issue.student.name}. Due date: {issue.due_date}')
            return redirect('home')
        else:
            messages.error(request, f'✗ Book "{issue.book.title}" is not available. No copies left in stock.')
            form.add_error('book', 'This book is not available. No copies left in stock.')
    else:
        # Display validation errors as warning messages
        for field, errors in form.errors.items():
            for error in errors:
                if 'not available' in error.lower() or 'no copies' in error.lower():
                    messages.error(request, f'✗ {error}')
                elif 'unreturned' in error.lower() or 'already has' in error.lower():
                    messages.warning(request, f'⚠ {error}')
                else:
                    messages.error(request, f'❌ {error}')

    return render(request, 'library_app/issue_book.html', {'form': form})

def student_detail(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        messages.error(request, 'Student not found.')
        return redirect('search_student')
    
    issued_books = IssueBook.objects.filter(student=student)
    notifications = Notification.objects.filter(student=student).order_by('-created_at')[:10]  # Last 10 notifications

    return render(request, 'student_detail.html', {
        'student': student,
        'issued_books': issued_books,
        'notifications': notifications
    })


def return_book(request, issue_id):
    try:
        issue = IssueBook.objects.get(id=issue_id)
    except IssueBook.DoesNotExist:
        messages.error(request, 'Book issue record not found.')
        return redirect('home')
    
    if not issue.is_returned:
        issue.is_returned = True
        issue.return_date = date.today()
        
        # Calculate fine before saving (while still marked as not returned)
        days_late = issue.days_overdue()
        fine = days_late * 10 if days_late > 0 else 0
        issue.fine_amount = fine
        
        issue.save()
        # Increase available quantity using the model method
        issue.book.return_book()
        
        # Create notification
        if fine > 0:
            message = f'Book "{issue.book.title}" has been returned. Fine: ₹{fine} ({days_late} days late)'
            messages.warning(request, f'✓ {message}')
        else:
            message = f'Book "{issue.book.title}" has been returned successfully.'
            messages.success(request, f'✓ {message}')
        
        Notification.objects.create(
            student=issue.student,
            issue_book=issue,
            message=message,
            notification_type='returned'
        )
        
        # Send email notification
        try:
            email_subject = 'Library Book Return Confirmation'
            if fine > 0:
                email_message = f'Dear {issue.student.name},\n\n{message}\n\nReturn Date: {issue.return_date}\n\nPlease pay the fine at the earliest.\n\nLibrary Management System'
            else:
                email_message = f'Dear {issue.student.name},\n\n{message}\n\nReturn Date: {issue.return_date}\n\nThank you for returning the book on time!\n\nLibrary Management System'
            
            send_mail(
                subject=email_subject,
                message=email_message,
                from_email=None,
                recipient_list=[issue.student.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send email: {e}")
        
    return redirect('student_detail', student_id=issue.student.id)


def issue_list(request):
    issues = IssueBook.objects.all()
    return render(request, 'student_detail.html', {'issues': issues})

def search_student(request):
    form = StudentSearchForm(request.GET or None)
    students = []
    
    if form.is_valid() and request.GET.get('search_query'):
        search_query = form.cleaned_data['search_query']
        # Search by name or roll number (case-insensitive)
        students = Student.objects.filter(
            Q(name__icontains=search_query) | 
            Q(roll_no__icontains=search_query)
        )
    else:
        # Show all students by default
        students = Student.objects.all()
    
    return render(request, 'search_student.html', {
        'form': form,
        'students': students
    })

def book_list(request):
    books = Book.objects.all().order_by('title')
    
    # Pagination
    paginator = Paginator(books, 10)  # Show 10 books per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'book_list.html', {
        'page_obj': page_obj
    })

