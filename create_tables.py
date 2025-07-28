import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Check what tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    all_tables = cursor.fetchall()
    print("All tables in database:")
    for table in all_tables:
        print(f"  - {table[0]}")
    
    # Check specifically for ai_interviewer tables
    ai_tables = [table[0] for table in all_tables if 'ai_interviewer' in table[0]]
    print(f"\nAI Interviewer tables: {ai_tables}")
    
    if not ai_tables:
        print("\nCreating tables manually...")
        # Create tables directly
        cursor.execute('''
            CREATE TABLE ai_interviewer_interviewsession (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                job_role VARCHAR(100) NOT NULL,
                session_type VARCHAR(50) NOT NULL,
                created_at DATETIME NOT NULL,
                completed_at DATETIME,
                overall_feedback TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (user_id) REFERENCES auth_user (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE ai_interviewer_interviewquestion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                question_type VARCHAR(50) NOT NULL DEFAULT 'theory',
                created_at DATETIME NOT NULL,
                FOREIGN KEY (session_id) REFERENCES ai_interviewer_interviewsession (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE ai_interviewer_useranswer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL UNIQUE,
                answer_text TEXT NOT NULL,
                feedback TEXT,
                rating INTEGER,
                suggested_improvement TEXT,
                weaknesses TEXT,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (question_id) REFERENCES ai_interviewer_interviewquestion (id)
            )
        ''')
        
        print("Tables created successfully!")
    else:
        print("Tables already exist")
