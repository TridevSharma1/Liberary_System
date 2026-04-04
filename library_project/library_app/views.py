from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Student, Book, IssueBook
from .forms import StudentForm, BookForm, IssueBookForm, StudentSearchForm

def home(request):
    return render(request, 'home.html')


def add_student(request):
    form = StudentForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('home')
    return render(request, 'add_student.html', {'form': form})


def add_book(request):
    form = BookForm(request.POST or None)
    if form.is_valid():
        form.save()
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

        issue.save()

        # Mark book unavailable
        issue.book.available = False
        issue.book.save()

        return redirect('home')

    return render(request, 'library_app/issue_book.html', {'form': form})

def student_detail(request, student_id):
    student = Student.objects.get(id=student_id)
    issued_books = IssueBook.objects.filter(student=student)

    return render(request, 'student_detail.html', {
        'student': student,
        'issued_books': issued_books
    })


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

