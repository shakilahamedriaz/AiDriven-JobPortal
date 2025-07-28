from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'company_name', 'location', 'description', 'requirements', 'is_featured']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'company_name': forms.TextInput(attrs={'class': 'form-input'}),
            'location': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'requirements': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
        labels = {
            'is_featured': 'Mark as Featured Job',
        }
        help_texts = {
            'is_featured': 'Featured jobs appear prominently on the homepage',
            'requirements': 'List the required skills, experience, and qualifications',
        }
