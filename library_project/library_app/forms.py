from django import forms
from .models import Student, Book, IssueBook
from django.contrib.auth.models import User
from .models import Profile
from django.core.exceptions import ValidationError

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Student.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('A student with this email already exists.')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise ValidationError('Phone number must contain only digits.')
        return phone


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
    
    def clean_total_quantity(self):
        total_quantity = self.cleaned_data.get('total_quantity')
        if total_quantity and total_quantity < 0:
            raise ValidationError('Total quantity cannot be negative.')
        return total_quantity
    
    def clean_available_quantity(self):
        available_quantity = self.cleaned_data.get('available_quantity')
        if available_quantity and available_quantity < 0:
            raise ValidationError('Available quantity cannot be negative.')
        return available_quantity
    
    def clean(self):
        cleaned_data = super().clean()
        total_quantity = cleaned_data.get('total_quantity')
        available_quantity = cleaned_data.get('available_quantity')
        
        if total_quantity and available_quantity:
            if available_quantity > total_quantity:
                raise ValidationError('Available quantity cannot exceed total quantity.')
        
        return cleaned_data


class IssueBookForm(forms.ModelForm):
    class Meta:
        model = IssueBook
        fields = ['student', 'book', 'due_date']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'book': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default due date to 7 days from now
        from datetime import date, timedelta
        if not self.instance.pk:  # Only for new instances
            self.fields['due_date'].initial = date.today() + timedelta(days=7)
        # Make due_date required
        self.fields['due_date'].required = True
    
    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        student = cleaned_data.get('student')
        
        # Check if student already has an unreturned copy of this book
        if student and book:
            existing_issue = IssueBook.objects.filter(
                student=student,
                book=book,
                is_returned=False
            ).exists()
            if existing_issue:
                raise ValidationError('This student already has an unreturned copy of this book.')
        
        return cleaned_data

class StudentSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name or roll number...'
        })
    )
