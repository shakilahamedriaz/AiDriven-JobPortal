from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from .forms import SignUpForm
from django.urls import reverse_lazy

def signup(request):
    from apps.jobs.models import Employer
    from apps.applicants.models import Applicant
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.role == 'employer':
                Employer.objects.create(user=user)
            else:
                Applicant.objects.create(user=user)
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'role'):
            if user.role == 'employer':
                return reverse_lazy('employer_dashboard')
            elif user.role == 'applicant':
                return reverse_lazy('applicant_dashboard')
        return reverse_lazy('home') # Default redirect

