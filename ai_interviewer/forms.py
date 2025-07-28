from django import forms
from .models import InterviewSession

class InterviewSessionForm(forms.ModelForm):
    class Meta:
        model = InterviewSession
        fields = ['job_role', 'session_type']
        widgets = {
            'job_role': forms.TextInput(attrs={'placeholder': 'e.g., Frontend Developer'}),
            'session_type': forms.Select(),
        }

class InterviewSetupForm(forms.Form):
    JOB_ROLE_CHOICES = [
        ('frontend_developer', 'Frontend Developer'),
        ('backend_developer', 'Backend Developer'),
        ('fullstack_developer', 'Full-Stack Developer'),
        ('data_scientist', 'Data Scientist'),
        ('devops_engineer', 'DevOps Engineer'),
        ('mobile_developer', 'Mobile Developer'),
        ('ui_ux_designer', 'UI/UX Designer'),
        ('product_manager', 'Product Manager'),
        ('qa_engineer', 'QA Engineer'),
        ('data_analyst', 'Data Analyst'),
    ]
    
    SESSION_TYPE_CHOICES = [
        ('theoretical', 'Theoretical Q&A'),
        ('problem-solving', 'Problem Solving'),
        ('database', 'Database Focused'),
        ('mcq', 'Quick MCQs'),
    ]

    job_role = forms.ChoiceField(
        choices=JOB_ROLE_CHOICES, 
        label="Select Job Role",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    session_type = forms.ChoiceField(
        choices=SESSION_TYPE_CHOICES, 
        label="Select Session Type",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
