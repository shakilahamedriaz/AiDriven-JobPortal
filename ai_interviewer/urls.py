from django.urls import path
from . import views

app_name = 'ai_interviewer'

urlpatterns = [
    path('', views.start_interview, name='start_interview'),
    path('setup/', views.start_interview, name='setup_interview'),
    path('session/<int:session_id>/', views.interview_session, name='interview_session'),
    path('results/<int:session_id>/', views.interview_results, name='interview_results'),
    path('voice/', views.voice_answer, name='voice_answer'),
    path('history/', views.user_interviews, name='user_interviews'),
]