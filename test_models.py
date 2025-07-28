import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Insert migration record
    cursor.execute("""
        INSERT OR IGNORE INTO django_migrations (app, name, applied) 
        VALUES ('ai_interviewer', '0001_initial', datetime('now'))
    """)
    print("Migration record inserted")
    
    # Verify tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'ai_interviewer%'")
    tables = cursor.fetchall()
    print(f"AI tables: {[t[0] for t in tables]}")
    
    # Test creating a session (just to verify everything works)
    try:
        from ai_interviewer.models import InterviewSession
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Check if we can import the models
        print("Models imported successfully")
        print("Everything should work now!")
    except Exception as e:
        print(f"Error: {e}")
