from django.urls import path, include
from . import views
from .views import CustomLoginView

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', CustomLoginView.as_view(template_name='registration/login.html'), name='login'),
]
