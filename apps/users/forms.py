from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import User
import re

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'your.email@example.com'
        }),
        help_text="We'll never share your email with anyone else."
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'John'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Doe'
        })
    )
    
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'johndoe123'
        }),
        help_text="Username must be 3-150 characters long and contain only letters, numbers, and @/./+/-/_ characters."
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Create a strong password'
        }),
        help_text="""
        <div class='password-requirements'>
            <p class='text-sm text-gray-600 mb-2'>Your password must contain:</p>
            <ul class='text-xs text-gray-500 space-y-1'>
                <li id='length-req' class='requirement'>✗ At least 8 characters</li>
                <li id='uppercase-req' class='requirement'>✗ At least one uppercase letter</li>
                <li id='lowercase-req' class='requirement'>✗ At least one lowercase letter</li>
                <li id='number-req' class='requirement'>✗ At least one number</li>
                <li id='special-req' class='requirement'>✗ At least one special character (!@#$%^&*)</li>
            </ul>
        </div>
        """
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your password'
        }),
        help_text="Enter the same password as before, for verification."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'})
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters long.")
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken. Please choose another one.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        
        # Custom password validation
        if len(password1) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        
        if not re.search(r'[A-Z]', password1):
            raise ValidationError("Password must contain at least one uppercase letter.")
        
        if not re.search(r'[a-z]', password1):
            raise ValidationError("Password must contain at least one lowercase letter.")
        
        if not re.search(r'\d', password1):
            raise ValidationError("Password must contain at least one number.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
            raise ValidationError("Password must contain at least one special character (!@#$%^&*).")
        
        # Check for common weak passwords
        weak_passwords = ['password', '12345678', 'qwerty123', 'admin123', 'password123']
        if password1.lower() in weak_passwords:
            raise ValidationError("This password is too common. Please choose a more secure password.")
        
        try:
            validate_password(password1)
        except ValidationError as e:
            raise ValidationError(e.messages)
        
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("The two password fields must match.")
        
        return password2

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        
        if not role:
            raise ValidationError("Please select your role.")
        
        return cleaned_data
