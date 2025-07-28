from django.shortcuts import render, redirect
from django.views.generic import CreateView, ListView
from .models import Application, Applicant
from apps.jobs.models import Job
from .forms import ApplicationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

class ApplicantRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'applicant'

    def handle_no_permission(self):
        if self.request.user.is_authenticated and self.request.user.role == 'employer':
            return render(self.request, 'applicants/employer_cant_apply.html')
        return super().handle_no_permission()

class ApplicationCreateView(LoginRequiredMixin, ApplicantRequiredMixin, CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'applicants/apply_job.html'
    
    def get_success_url(self):
        return '/applicants/dashboard'

    def form_valid(self, form):
        form.instance.applicant = Applicant.objects.get(user=self.request.user)
        form.instance.job = Job.objects.get(pk=self.kwargs['job_pk'])
        return super().form_valid(form)

class ApplicantDashboardView(LoginRequiredMixin, ApplicantRequiredMixin, ListView):
    model = Application
    template_name = 'applicants/applicant_dashboard.html'
    context_object_name = 'applications'

    def get_queryset(self):
        return Application.objects.filter(applicant__user=self.request.user)

def view_applicants(request, job_pk):
    applications = Application.objects.filter(job_id=job_pk)
    return render(request, 'applicants/view_applicants.html', {'applications': applications})
