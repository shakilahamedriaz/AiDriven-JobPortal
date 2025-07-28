import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
django.setup()

from django.db import connection

# Fix the database constraint issue
with connection.cursor() as cursor:
    cursor.execute("UPDATE ai_interviewer_interviewsession SET overall_feedback = '' WHERE overall_feedback IS NULL")
    print("Updated null values in overall_feedback field")
    
    # Check if we need to modify the constraint (SQLite doesn't support direct constraint modification)
    # So we'll handle this in the model by providing a default value
    print("Database updated successfully")
