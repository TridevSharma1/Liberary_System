from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-student/', views.add_student, name='add_student'),
    path('update-student/<int:student_id>/', views.update_student, name='update_student'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('add-book/', views.add_book, name='add_book'),
    path('issue-book/', views.issue_book, name='issue_book'),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('return-book/<int:issue_id>/', views.return_book, name='return_book'),
    path('search-student/', views.search_student, name='search_student'),
    path('books/', views.book_list, name='book_list'),
]