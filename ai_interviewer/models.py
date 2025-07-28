from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class InterviewSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job_role = models.CharField(max_length=100)
    session_type = models.CharField(max_length=50, choices=[
        ('theoretical', 'Theoretical Q&A'),
        ('database', 'Database Focused'),
        ('problem-solving', 'Problem Solving'),
        ('mcq', 'Quick MCQs'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    overall_feedback = models.TextField(blank=True, default='')

    def __str__(self):
        return f"Interview for {self.user.username} - {self.job_role}"

class InterviewQuestion(models.Model):
    session = models.ForeignKey(InterviewSession, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    ai_hint = models.TextField(blank=True, null=True, help_text="AI-generated hint for the question")
    difficulty_level = models.CharField(max_length=20, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ], default='medium')
    question_type = models.CharField(max_length=50, choices=[
        ('theory', 'Theory'),
        ('coding', 'Coding'),
        ('mcq', 'Multiple Choice'),
    ], default='theory')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text[:50] + "..."

class UserAnswer(models.Model):
    question = models.OneToOneField(InterviewQuestion, related_name='answer', on_delete=models.CASCADE)
    answer_text = models.TextField()
    feedback = models.TextField(blank=True, null=True)
    rating = models.IntegerField(null=True, blank=True)
    suggested_improvement = models.TextField(blank=True, null=True)
    weaknesses = models.TextField(blank=True, null=True)
    strengths = models.TextField(blank=True, null=True)
    time_taken = models.IntegerField(null=True, blank=True, help_text="Time taken in seconds")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer to: {self.question.question_text[:30]}..."
    
    def get_rating_color(self):
        if self.rating >= 8:
            return 'green'
        elif self.rating >= 6:
            return 'yellow'
        else:
            return 'red'
    
    def get_rating_text(self):
        if self.rating >= 8:
            return 'Excellent'
        elif self.rating >= 6:
            return 'Good'
        else:
            return 'Needs Improvement'