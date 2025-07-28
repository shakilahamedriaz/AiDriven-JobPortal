from django.contrib import admin

from django.contrib import admin
from .models import InterviewSession, InterviewQuestion, UserAnswer

admin.site.register(InterviewSession)
admin.site.register(InterviewQuestion)
admin.site.register(UserAnswer)

