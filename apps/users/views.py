from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from .forms import SignUpForm
from django.urls import reverse_lazy

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import SignUpForm

def signup(request):
    from apps.jobs.models import Employer
    from apps.applicants.models import Applicant
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                if user.role == 'employer':
                    Employer.objects.create(user=user)
                    messages.success(
                        request, 
                        f'🎉 Welcome aboard, {user.first_name}! Your employer account has been created successfully. Please sign in to start posting jobs and finding amazing talent!'
                    )
                else:
                    Applicant.objects.create(user=user)
                    messages.success(
                        request, 
                        f'🚀 Welcome to JobPortal, {user.first_name}! Your account has been created successfully. Please sign in to start exploring thousands of job opportunities!'
                    )
                
                # Redirect to login page with success message
                return redirect('login')
                    
            except Exception as e:
                messages.error(
                    request, 
                    '❌ Something went wrong while creating your account. Please try again or contact support if the problem persists.'
                )
        else:
            # Add custom error messages for better UX
            if form.errors:
                messages.error(
                    request, 
                    '⚠️ Please fix the errors below and try again.'
                )
    else:
        form = SignUpForm()
    
    return render(request, 'registration/signup.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        
        # Add success message based on user role
        if hasattr(user, 'role'):
            if user.role == 'employer':
                messages.success(
                    self.request, 
                    f'🎯 Welcome back, {user.first_name}! Ready to discover amazing talent and manage your job postings.'
                )
            elif user.role == 'applicant':
                messages.success(
                    self.request, 
                    f'✨ Great to see you again, {user.first_name}! Let\'s find your next career opportunity together.'
                )
        else:
            messages.success(
                self.request, 
                f'👋 Welcome back, {user.first_name}! You\'ve successfully signed in.'
            )
        
        return response

    def get_success_url(self):
        # Always redirect to home page to show success message
        # Users can then navigate to their dashboard from the navbar
        return reverse_lazy('home')

