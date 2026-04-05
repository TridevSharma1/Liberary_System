from django.contrib import admin
from .models import Student, Book, IssueBook

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'roll_no', 'email', 'phone']
    search_fields = ['name', 'roll_no', 'email']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'total_quantity', 'available_quantity', 'available']
    search_fields = ['title', 'author', 'isbn']
    readonly_fields = ['available']
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'author', 'isbn')
        }),
        ('Inventory', {
            'fields': ('total_quantity', 'available_quantity', 'available')
        }),
    )

@admin.register(IssueBook)
class IssueBookAdmin(admin.ModelAdmin):
    list_display = ['student', 'book', 'issue_date', 'return_date', 'is_returned']
    search_fields = ['student__name', 'book__title']
    list_filter = ['is_returned', 'issue_date']
    readonly_fields = ['issue_date']