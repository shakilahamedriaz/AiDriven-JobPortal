from django.urls import path
from .views import JobListView, JobDetailView, JobCreateView, employer_dashboard

urlpatterns = [
    path('', JobListView.as_view(), name='job_list'),
    path('<int:pk>/', JobDetailView.as_view(), name='job_detail'),
    path('post/', JobCreateView.as_view(), name='post_job'),
    path('dashboard/', employer_dashboard, name='employer_dashboard'),
]
