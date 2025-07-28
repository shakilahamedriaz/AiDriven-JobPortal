from django.urls import path
from .views import ApplicationCreateView, ApplicantDashboardView, view_applicants

urlpatterns = [
    path('apply/<int:job_pk>/', ApplicationCreateView.as_view(), name='apply_job'),
    path('dashboard/', ApplicantDashboardView.as_view(), name='applicant_dashboard'),
    path('view/<int:job_pk>/', view_applicants, name='view_applicants'),
]
