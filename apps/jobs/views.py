from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView
from .models import Job, Employer
from .forms import JobForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

class EmployerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'employer'

class JobListView(ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        queryset = super().get_queryset()
        title = self.request.GET.get('title')
        company = self.request.GET.get('company')
        location = self.request.GET.get('location')
        if title:
            queryset = queryset.filter(title__icontains=title)
        if company:
            queryset = queryset.filter(company_name__icontains=company)
        if location:
            queryset = queryset.filter(location__icontains=location)
        return queryset

class JobDetailView(DetailView):
    model = Job
    template_name = 'jobs/job_detail.html'

class JobCreateView(LoginRequiredMixin, EmployerRequiredMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = 'jobs/post_job.html'

    def form_valid(self, form):
        form.instance.posted_by = Employer.objects.get(user=self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('job_list')

def employer_dashboard(request):
    if request.user.is_authenticated and request.user.role == 'employer':
        jobs = Job.objects.filter(posted_by__user=request.user)
        return render(request, 'jobs/employer_dashboard.html', {'jobs': jobs})
    else:
        return redirect('home')

def home(request):
    return redirect('job_list')
