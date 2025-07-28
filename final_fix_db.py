#!/usr/bin/env python
import os
import django
import sqlite3

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
django.setup()

from ai_interviewer.models import InterviewSession, InterviewQuestion, UserAnswer

def create_tables():
    """Create the ai_interviewer tables directly via SQL"""
    db_path = 'db.sqlite3'
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Drop existing tables if they exist (to ensure clean state)
        cursor.execute('DROP TABLE IF EXISTS ai_interviewer_useranswer')
        cursor.execute('DROP TABLE IF EXISTS ai_interviewer_interviewquestion')
        cursor.execute('DROP TABLE IF EXISTS ai_interviewer_interviewsession')
        
        # Create InterviewSession table
        cursor.execute('''
            CREATE TABLE ai_interviewer_interviewsession (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES auth_user(id),
                role VARCHAR(200) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'active',
                overall_feedback TEXT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL
            )
        ''')
        
        # Create InterviewQuestion table
        cursor.execute('''
            CREATE TABLE ai_interviewer_interviewquestion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL REFERENCES ai_interviewer_interviewsession(id) ON DELETE CASCADE,
                question_text TEXT NOT NULL,
                question_order INTEGER NOT NULL
            )
        ''')
        
        # Create UserAnswer table
        cursor.execute('''
            CREATE TABLE ai_interviewer_useranswer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL REFERENCES ai_interviewer_interviewquestion(id) ON DELETE CASCADE,
                answer_text TEXT NOT NULL,
                ai_feedback TEXT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX idx_interviewsession_user ON ai_interviewer_interviewsession(user_id)')
        cursor.execute('CREATE INDEX idx_interviewquestion_session ON ai_interviewer_interviewquestion(session_id)')
        cursor.execute('CREATE INDEX idx_useranswer_question ON ai_interviewer_useranswer(question_id)')
        
        conn.commit()
        print("✅ All tables created successfully!")
        
        # Verify tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'ai_interviewer_%'")
        tables = cursor.fetchall()
        print(f"✅ Created tables: {[table[0] for table in tables]}")
        
        # Test Django models can access the tables
        from django.db import connection
        with connection.cursor() as django_cursor:
            django_cursor.execute("SELECT COUNT(*) FROM ai_interviewer_interviewsession")
            print("✅ Django can access InterviewSession table")
            
            django_cursor.execute("SELECT COUNT(*) FROM ai_interviewer_interviewquestion")  
            print("✅ Django can access InterviewQuestion table")
            
            django_cursor.execute("SELECT COUNT(*) FROM ai_interviewer_useranswer")
            print("✅ Django can access UserAnswer table")
        
        # Insert migration record to sync with Django
        cursor.execute('''
            INSERT OR REPLACE INTO django_migrations (app, name, applied) 
            VALUES ('ai_interviewer', '0001_initial', datetime('now'))
        ''')
        conn.commit()
        print("✅ Migration record inserted")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    create_tables()
