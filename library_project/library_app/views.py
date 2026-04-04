from django.shortcuts import render, redirect
from .models import Student, Book, IssueBook
from .forms import StudentForm, BookForm, IssueBookForm
from .models import Issue

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
    issues = Issue.objects.all()
    return render(request, 'student_detail.html', {'issues': issues})

from django.shortcuts import redirect, get_object_or_404

