import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'ai_interviewer%'")
    tables = cursor.fetchall()
    print("AI Interviewer tables:", tables)
    
    # Create tables manually if they don't exist
    if not tables:
        print("No ai_interviewer tables found. Creating them...")
        from ai_interviewer.models import InterviewSession, InterviewQuestion, UserAnswer
        from django.core.management import call_command
        
        # Force create the migration
        call_command('makemigrations', 'ai_interviewer', verbosity=0)
        call_command('migrate', 'ai_interviewer', verbosity=0)
        print("Tables created successfully!")
    else:
        print("Tables already exist")
