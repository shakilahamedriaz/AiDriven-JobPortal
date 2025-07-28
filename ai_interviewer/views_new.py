from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import InterviewSession, InterviewQuestion, UserAnswer
from .forms import InterviewSetupForm
from groq import Groq
import os
import json
import random

# Initialize Groq client
try:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except Exception as e:
    client = None
    print(f"Warning: Groq client initialization failed: {e}")
    print("Please set GROQ_API_KEY environment variable for AI functionality")

@login_required
def start_interview(request):
    """Start a new interview session"""
    if request.method == 'POST':
        form = InterviewSetupForm(request.POST)
        if form.is_valid():
            job_role = form.cleaned_data['job_role']
            session_type = form.cleaned_data['session_type']
            
            session = InterviewSession.objects.create(
                user=request.user,
                job_role=job_role,
                session_type=session_type,
                overall_feedback=''  # Initialize with empty string
            )
            
            return redirect('ai_interviewer:interview_session', session_id=session.id)
    else:
        form = InterviewSetupForm()
    
    return render(request, 'ai_interviewer/start_interview.html', {'form': form})

def generate_question(session, question_number):
    """Generate a new interview question"""
    try:
        if client:
            # Get previously asked questions to avoid repetition
            previous_questions = [q.question_text for q in session.questions.all()]
            
            # Create more detailed prompts based on session type and question number
            session_type_prompts = {
                'theoretical': f"Generate a theoretical question #{question_number} for a {session.job_role} interview. Focus on concepts, principles, and knowledge.",
                'problem-solving': f"Create a problem-solving question #{question_number} for a {session.job_role} interview. Present a realistic scenario or challenge.",
                'database': f"Generate a database-related question #{question_number} for a {session.job_role} interview. Focus on SQL, optimization, design, or architecture.",
                'mcq': f"Create a technical question #{question_number} for a {session.job_role} interview about tools, technologies, or best practices."
            }
            
            base_prompt = session_type_prompts.get(session.session_type, 
                f"Generate interview question #{question_number} for {session.job_role} position")
            
            if previous_questions:
                base_prompt += f" Make it different from these previous questions: {previous_questions}"
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are an expert technical interviewer with 10+ years of experience. 
                        {base_prompt}
                        
                        Guidelines:
                        - Make the question specific to {session.job_role}
                        - Ensure it's question #{question_number} in difficulty progression
                        - Keep it clear, professional, and interview-appropriate
                        - Only return the question text, nothing else
                        - Make it unique and different from previous questions"""
                    }
                ],
                model="llama3-8b-8192",
                temperature=0.8,  # Add randomness for variety
            )
            new_question_text = chat_completion.choices[0].message.content.strip()
            
            # Clean up the response (remove quotes, extra formatting)
            new_question_text = new_question_text.strip('"').strip("'").strip()
            
        else:
            # Enhanced fallback questions with variety
            fallback_questions = {
                'theoretical': [
                    f"What are the core principles every {session.job_role} should master?",
                    f"Explain the most important design patterns in {session.job_role}.",
                    f"What are the latest trends and technologies in {session.job_role}?",
                    f"How do you stay updated with {session.job_role} best practices?",
                    f"What are the common challenges faced by {session.job_role}s?"
                ],
                'problem-solving': [
                    f"Walk me through how you would debug a complex issue in {session.job_role}.",
                    f"How would you optimize a slow-performing system in {session.job_role}?",
                    f"Describe your approach to handling conflicting requirements in {session.job_role}.",
                    f"How do you prioritize tasks when everything seems urgent in {session.job_role}?",
                    f"Tell me about a time you had to learn a new technology quickly for {session.job_role}."
                ],
                'database': [
                    f"How would you design a database schema for {session.job_role} applications?",
                    f"Explain query optimization techniques relevant to {session.job_role}.",
                    f"What are the trade-offs between different database types in {session.job_role}?",
                    f"How do you handle data consistency in distributed systems for {session.job_role}?",
                    f"Describe your approach to database performance monitoring in {session.job_role}."
                ],
                'mcq': [
                    f"What tools and frameworks are essential for modern {session.job_role} work?",
                    f"Which testing strategies are most effective for {session.job_role}?",
                    f"What are the key metrics you track as a {session.job_role}?",
                    f"How do you ensure code quality and maintainability in {session.job_role}?",
                    f"What collaboration tools and practices do you use as a {session.job_role}?"
                ]
            }
            questions_list = fallback_questions.get(session.session_type, [f"Tell me about your experience as a {session.job_role}."])
            new_question_text = random.choice(questions_list)
            
        return InterviewQuestion.objects.create(
            session=session,
            question_text=new_question_text,
            question_type=session.session_type
        )
        
    except Exception as e:
        # Enhanced fallback questions if API fails
        fallback_questions = {
            'theoretical': [
                f"What are the core principles every {session.job_role} should master?",
                f"Explain the most important design patterns in {session.job_role}.",
                f"What are the latest trends and technologies in {session.job_role}?",
                f"How do you stay updated with {session.job_role} best practices?",
                f"What are the common challenges faced by {session.job_role}s?"
            ],
            'problem-solving': [
                f"Walk me through how you would debug a complex issue in {session.job_role}.",
                f"How would you optimize a slow-performing system in {session.job_role}?",
                f"Describe your approach to handling conflicting requirements in {session.job_role}.",
                f"How do you prioritize tasks when everything seems urgent in {session.job_role}?",
                f"Tell me about a time you had to learn a new technology quickly for {session.job_role}."
            ],
            'database': [
                f"How would you design a database schema for {session.job_role} applications?",
                f"Explain query optimization techniques relevant to {session.job_role}.",
                f"What are the trade-offs between different database types in {session.job_role}?",
                f"How do you handle data consistency in distributed systems for {session.job_role}?",
                f"Describe your approach to database performance monitoring in {session.job_role}."
            ],
            'mcq': [
                f"What tools and frameworks are essential for modern {session.job_role} work?",
                f"Which testing strategies are most effective for {session.job_role}?",
                f"What are the key metrics you track as a {session.job_role}?",
                f"How do you ensure code quality and maintainability in {session.job_role}?",
                f"What collaboration tools and practices do you use as a {session.job_role}?"
            ]
        }
        
        questions_list = fallback_questions.get(session.session_type, [f"Tell me about your experience as a {session.job_role}."])
        selected_question = random.choice(questions_list)
        
        return InterviewQuestion.objects.create(
            session=session,
            question_text=selected_question,
            question_type=session.session_type
        )

@login_required
def interview_session(request, session_id):
    """Handle the main interview session"""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    
    if request.method == 'POST':
        answer_text = request.POST.get('answer')
        question_id = request.POST.get('question_id')
        question = get_object_or_404(InterviewQuestion, id=question_id)
        
        # Use Groq to evaluate the answer
        try:
            if client:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are an expert interviewer. Evaluate this answer for a {session.job_role} {session.session_type} interview question. Provide feedback, rating (1-10), and suggestions for improvement. Format: Feedback: [your feedback] Rating: [1-10]/10 Improvements: [suggestions]"
                        },
                        {
                            "role": "user",
                            "content": f"Question: {question.question_text}\nAnswer: {answer_text}"
                        }
                    ],
                    model="llama3-8b-8192",
                )
                response_text = chat_completion.choices[0].message.content
                
                # Parse the response
                try:
                    feedback = response_text.split("Feedback:")[1].split("Rating:")[0].strip()
                    rating_str = response_text.split("Rating:")[1].split("Improvements:")[0].strip()
                    rating = int(''.join(filter(str.isdigit, rating_str.split('/')[0])))
                    improvements = response_text.split("Improvements:")[1].strip()
                except (IndexError, ValueError):
                    feedback = "Could not parse AI feedback. The raw response was: " + response_text
                    rating = 5
                    improvements = "N/A"
            else:
                # Fallback when Groq is not available
                feedback = "AI evaluation temporarily unavailable. Please review your answer manually."
                rating = 5
                improvements = "Set up Groq API key for AI feedback."

            UserAnswer.objects.create(
                question=question,
                answer_text=answer_text,
                feedback=feedback,
                rating=rating,
                suggested_improvement=improvements
            )
            
        except Exception as e:
            # Handle API errors gracefully
            UserAnswer.objects.create(
                question=question,
                answer_text=answer_text,
                feedback=f"Error getting AI feedback: {str(e)}",
                rating=5,
                suggested_improvement="Please try again later."
            )
        
        return redirect('ai_interviewer:interview_session', session_id=session.id)

    # GET request logic - Show interview interface
    questions = session.questions.order_by('created_at')
    answered_questions = questions.filter(answer__isnull=False)
    current_question = questions.filter(answer__isnull=True).first()
    
    # Generate first question if none exist
    if not questions.exists():
        current_question = generate_question(session, 1)
    
    # Check if interview is complete (5 questions answered)
    if answered_questions.count() >= 5:
        if not session.completed_at:
            session.completed_at = timezone.now()
            session.overall_feedback = f"Interview completed! You answered 5 questions for the {session.job_role} position."
            session.save()
        return redirect('ai_interviewer:interview_results', session_id=session.id)
    
    # Generate next question if current one is answered
    if not current_question and answered_questions.count() < 5:
        question_number = answered_questions.count() + 1
        current_question = generate_question(session, question_number)
    
    # Get last answered question for feedback display
    last_answered = answered_questions.last()
    
    context = {
        'session': session,
        'question': current_question,
        'last_answered': last_answered,
        'question_number': answered_questions.count() + 1,
        'total_questions': 5,
        'progress_percentage': (answered_questions.count() / 5) * 100
    }
    return render(request, 'ai_interviewer/interview_session.html', context)

@login_required
def interview_results(request, session_id):
    """Display interview results and analytics"""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    answered_questions = session.questions.filter(answer__isnull=False).prefetch_related('answer')
    
    # Calculate average rating
    ratings = [q.answer.rating for q in answered_questions if q.answer.rating is not None]
    average_rating = sum(ratings) / len(ratings) if ratings else 0
    
    # Calculate performance metrics
    total_questions = answered_questions.count()
    strong_answers = len([r for r in ratings if r >= 7])
    weak_answers = len([r for r in ratings if r < 5])
    
    context = {
        'session': session,
        'answered_questions': answered_questions,
        'average_rating': round(average_rating, 1),
        'total_questions': total_questions,
        'strong_answers': strong_answers,
        'weak_answers': weak_answers,
        'completion_percentage': 100 if session.completed_at else 0
    }
    return render(request, 'ai_interviewer/interview_results.html', context)

@login_required
def user_interviews(request):
    """Display user's interview history"""
    sessions = InterviewSession.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'ai_interviewer/user_interviews.html', {'sessions': sessions})

@csrf_exempt
def voice_answer(request):
    """Handle voice answers via AJAX"""
    if request.method == 'POST':
        data = json.loads(request.body)
        answer_text = data.get('answer')
        question_id = data.get('question_id')
        
        try:
            question = InterviewQuestion.objects.get(id=question_id)
            session = question.session
            
            if client:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are an expert interviewer. Evaluate this answer for a {session.job_role} {session.session_type} interview question. Provide feedback, rating (1-10), and suggestions for improvement. Format: Feedback: [your feedback] Rating: [1-10]/10 Improvements: [suggestions]"
                        },
                        {
                            "role": "user",
                            "content": f"Question: {question.question_text}\nAnswer: {answer_text}"
                        }
                    ],
                    model="llama3-8b-8192",
                )
                response_text = chat_completion.choices[0].message.content
                
                # Parse the response
                try:
                    feedback = response_text.split("Feedback:")[1].split("Rating:")[0].strip()
                    rating_str = response_text.split("Rating:")[1].split("Improvements:")[0].strip()
                    rating = int(''.join(filter(str.isdigit, rating_str.split('/')[0])))
                    improvements = response_text.split("Improvements:")[1].strip()
                except (IndexError, ValueError):
                    feedback = "Could not parse AI feedback"
                    rating = 5
                    improvements = "N/A"
            else:
                feedback = "AI evaluation temporarily unavailable"
                rating = 5
                improvements = "Set up Groq API key for AI feedback"

            UserAnswer.objects.create(
                question=question,
                answer_text=answer_text,
                feedback=feedback,
                rating=rating,
                suggested_improvement=improvements
            )
            
            return JsonResponse({
                'success': True,
                'feedback': feedback,
                'rating': rating,
                'improvements': improvements
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})
