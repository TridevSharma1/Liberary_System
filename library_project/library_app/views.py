from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Student, Book, IssueBook
from .forms import StudentForm, BookForm, IssueBookForm, StudentSearchForm
from django.contrib import messages

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

        # Auto return date (7 days later)
        if not issue.return_date:
            issue.return_date = date.today() + timedelta(days=7)

        # Attempt to issue the book and decrease quantity
        if issue.book.issue_book():
            issue.save()
            messages.success(request, f'✓ Book "{issue.book.title}" has been issued to {issue.student.name}. Return by: {issue.return_date}')
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
    student = Student.objects.get(id=student_id)
    issued_books = IssueBook.objects.filter(student=student)

    return render(request, 'student_detail.html', {
        'student': student,
        'issued_books': issued_books
    })


def return_book(request, issue_id):
    issue = IssueBook.objects.get(id=issue_id)
    if not issue.is_returned:
        issue.is_returned = True
        issue.save()
        # Increase available quantity using the model method
        issue.book.return_book()
        messages.success(request, f'✓ Book "{issue.book.title}" has been returned by {issue.student.name}.')
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

