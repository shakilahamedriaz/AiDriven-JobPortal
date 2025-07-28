from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
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

def generate_question(session, question_number):
    """Generate a new interview question with AI hint"""
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
            
            # Generate question
            question_completion = client.chat.completions.create(
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
                temperature=0.8,
            )
            new_question_text = question_completion.choices[0].message.content.strip().strip('"').strip("'")
            
            # Generate AI hint
            hint_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": f"""For this {session.job_role} interview question: "{new_question_text}"
                        
                        Provide a helpful hint that:
                        - Guides the thinking process without giving away the answer
                        - Suggests what areas to cover or approach to take
                        - Is encouraging and constructive
                        - Is 1-2 sentences long
                        
                        Only return the hint text, nothing else."""
                    }
                ],
                model="llama3-8b-8192",
                temperature=0.7,
            )
            ai_hint = hint_completion.choices[0].message.content.strip().strip('"').strip("'")
            
            # Determine difficulty based on question number
            difficulty_mapping = {1: 'easy', 2: 'easy', 3: 'medium', 4: 'medium', 5: 'hard'}
            difficulty = difficulty_mapping.get(question_number, 'medium')
            
        else:
            # Enhanced fallback questions with hints
            fallback_data = {
                'theoretical': [
                    {
                        'question': f"What are the core principles every {session.job_role} should master?",
                        'hint': "Think about fundamental concepts, best practices, and key methodologies in your field."
                    },
                    {
                        'question': f"Explain the most important design patterns in {session.job_role}.",
                        'hint': "Consider patterns that solve common problems and improve code maintainability."
                    },
                    {
                        'question': f"What are the latest trends and technologies in {session.job_role}?",
                        'hint': "Focus on recent developments and their practical applications in the industry."
                    },
                    {
                        'question': f"How do you stay updated with {session.job_role} best practices?",
                        'hint': "Think about learning resources, communities, and professional development methods."
                    },
                    {
                        'question': f"What are the common challenges faced by {session.job_role}s?",
                        'hint': "Consider technical, communication, and project management challenges."
                    }
                ],
                'problem-solving': [
                    {
                        'question': f"Walk me through how you would debug a complex issue in {session.job_role}.",
                        'hint': "Think about systematic approaches, tools, and methodologies you would use."
                    },
                    {
                        'question': f"How would you optimize a slow-performing system in {session.job_role}?",
                        'hint': "Consider identification methods, bottleneck analysis, and optimization strategies."
                    },
                    {
                        'question': f"Describe your approach to handling conflicting requirements in {session.job_role}.",
                        'hint': "Think about stakeholder communication, priority setting, and compromise strategies."
                    },
                    {
                        'question': f"How do you prioritize tasks when everything seems urgent in {session.job_role}?",
                        'hint': "Consider frameworks for prioritization and communication with stakeholders."
                    },
                    {
                        'question': f"Tell me about a time you had to learn a new technology quickly for {session.job_role}.",
                        'hint': "Use the STAR method: Situation, Task, Action, Result."
                    }
                ],
                'database': [
                    {
                        'question': f"How would you design a database schema for {session.job_role} applications?",
                        'hint': "Think about normalization, relationships, performance, and scalability considerations."
                    },
                    {
                        'question': f"Explain query optimization techniques relevant to {session.job_role}.",
                        'hint': "Consider indexing, query structure, execution plans, and database-specific optimizations."
                    },
                    {
                        'question': f"What are the trade-offs between different database types in {session.job_role}?",
                        'hint': "Compare SQL vs NoSQL, considering use cases, consistency, and scalability."
                    },
                    {
                        'question': f"How do you handle data consistency in distributed systems for {session.job_role}?",
                        'hint': "Think about ACID properties, CAP theorem, and consistency patterns."
                    },
                    {
                        'question': f"Describe your approach to database performance monitoring in {session.job_role}.",
                        'hint': "Consider metrics to track, tools to use, and proactive vs reactive monitoring."
                    }
                ],
                'mcq': [
                    {
                        'question': f"What tools and frameworks are essential for modern {session.job_role} work?",
                        'hint': "Think about development, testing, deployment, and monitoring tools."
                    },
                    {
                        'question': f"Which testing strategies are most effective for {session.job_role}?",
                        'hint': "Consider different types of testing and their appropriate use cases."
                    },
                    {
                        'question': f"What are the key metrics you track as a {session.job_role}?",
                        'hint': "Think about both technical and business metrics that matter."
                    },
                    {
                        'question': f"How do you ensure code quality and maintainability in {session.job_role}?",
                        'hint': "Consider practices, tools, and processes that support clean code."
                    },
                    {
                        'question': f"What collaboration tools and practices do you use as a {session.job_role}?",
                        'hint': "Think about communication, version control, and project management tools."
                    }
                ]
            }
            
            questions_list = fallback_data.get(session.session_type, [
                {'question': f"Tell me about your experience as a {session.job_role}.", 'hint': "Structure your answer chronologically and highlight key achievements."}
            ])
            selected_data = random.choice(questions_list)
            new_question_text = selected_data['question']
            ai_hint = selected_data['hint']
            difficulty = 'medium'
            
        return InterviewQuestion.objects.create(
            session=session,
            question_text=new_question_text,
            ai_hint=ai_hint,
            difficulty_level=difficulty,
            question_type=session.session_type
        )
        
    except Exception as e:
        # Enhanced fallback questions if API fails
        fallback_data = {
            'theoretical': [
                {
                    'question': f"What are the core principles every {session.job_role} should master?",
                    'hint': "Think about fundamental concepts, best practices, and key methodologies in your field."
                },
                {
                    'question': f"Explain the most important design patterns in {session.job_role}.",
                    'hint': "Consider patterns that solve common problems and improve code maintainability."
                }
            ]
        }
        
        questions_list = fallback_data.get(session.session_type, [
            {'question': f"Tell me about your experience as a {session.job_role}.", 'hint': "Structure your answer chronologically and highlight key achievements."}
        ])
        selected_data = random.choice(questions_list)
        
        return InterviewQuestion.objects.create(
            session=session,
            question_text=selected_data['question'],
            ai_hint=selected_data['hint'],
            difficulty_level='medium',
            question_type=session.session_type
        )

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

@login_required
def interview_session(request, session_id):
    """Handle the main interview session"""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    
    if request.method == 'POST':
        answer_text = request.POST.get('answer')
        question_id = request.POST.get('question_id')
        question = get_object_or_404(InterviewQuestion, id=question_id)
        
        # Use Groq to evaluate the answer with comprehensive analysis
        try:
            if client:
                evaluation_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": f"""You are an expert {session.job_role} interviewer evaluating this answer:
                            
                            Question: "{question.question_text}"
                            Answer: "{answer_text}"
                            Difficulty: {question.difficulty_level}
                            Session Type: {session.session_type}
                            
                            Provide a comprehensive evaluation with this EXACT format:
                            
                            Feedback: [Detailed constructive feedback about the answer quality, accuracy, and completeness]
                            Rating: [Single number from 1-10]
                            Strengths: [What the candidate did well in their answer]
                            Improvements: [Specific suggestions for improvement]
                            
                            Be professional, constructive, and specific. Consider the difficulty level and session type when rating."""
                        }
                    ],
                    model="llama3-8b-8192",
                    temperature=0.3,  # Lower temperature for consistent evaluation
                )
                response_text = evaluation_completion.choices[0].message.content
                
                # Parse the comprehensive response
                try:
                    feedback = response_text.split("Feedback:")[1].split("Rating:")[0].strip()
                    rating_str = response_text.split("Rating:")[1].split("Strengths:")[0].strip()
                    rating = int(''.join(filter(str.isdigit, rating_str.split('/')[0])))
                    strengths = response_text.split("Strengths:")[1].split("Improvements:")[0].strip()
                    improvements = response_text.split("Improvements:")[1].strip()
                except (IndexError, ValueError):
                    # Fallback parsing if format doesn't match
                    feedback = "Could not parse detailed AI feedback. Raw response: " + response_text[:200] + "..."
                    rating = 5
                    strengths = "Response provided"
                    improvements = "Please provide more detailed answers"
            else:
                # Enhanced fallback evaluation
                word_count = len(answer_text.split())
                feedback = f"Thank you for your {word_count}-word response. "
                
                if word_count > 100:
                    feedback += "Your answer is comprehensive and detailed."
                    rating = 7
                elif word_count > 50:
                    feedback += "Your answer covers the key points."
                    rating = 6
                else:
                    feedback += "Consider providing more detailed examples and explanations."
                    rating = 5
                
                strengths = "Clear communication" if word_count > 30 else "Concise response"
                improvements = "Set up Groq API key for detailed AI evaluation and feedback."

            UserAnswer.objects.create(
                question=question,
                answer_text=answer_text,
                feedback=feedback,
                rating=rating,
                strengths=strengths,
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

    # GET request logic
    questions = session.questions.order_by('created_at')
    answered_questions = questions.filter(answer__isnull=False)
    current_question = questions.filter(answer__isnull=True).first()
    
    # Generate first question if no questions exist
    if not questions.exists():
        current_question = generate_question(session, 1)
    
    # Check if session should be completed (limit to 5 questions)
    if answered_questions.count() >= 5:
        print(f"DEBUG: Session {session.id} completed with {answered_questions.count()} questions")
        if not session.completed_at:
            session.completed_at = timezone.now()
            
            # Generate overall feedback
            if client:
                try:
                    # Get all answers for overall feedback
                    all_answers = [(q.question_text, q.answer.answer_text, q.answer.rating) 
                                 for q in answered_questions if hasattr(q, 'answer')]
                    
                    feedback_prompt = f"Based on this {session.job_role} interview session, provide overall feedback. "
                    feedback_prompt += f"Questions and answers: {all_answers}. "
                    feedback_prompt += "Give a summary of strengths, areas for improvement, and next steps."
                    
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "system", "content": feedback_prompt}],
                        model="llama3-8b-8192",
                    )
                    session.overall_feedback = chat_completion.choices[0].message.content
                except Exception as e:
                    session.overall_feedback = f"Interview completed! You answered {answered_questions.count()} questions. Review your individual feedback for detailed insights."
            else:
                session.overall_feedback = f"Interview completed! You answered {answered_questions.count()} questions for the {session.job_role} position."
            
            session.save()
            print(f"DEBUG: Session {session.id} marked as completed at {session.completed_at}")
        
        print(f"DEBUG: Redirecting to results page for session {session.id}")
        return redirect('ai_interviewer:interview_results', session_id=session.id)
    
    # Generate next question if current one is answered but we haven't reached 5 questions
    if not current_question and answered_questions.count() < 5:
        question_number = answered_questions.count() + 1
        current_question = generate_question(session, question_number)
    
    # Get last answered question for feedback display
    last_answered = answered_questions.last()
    
    context = {
        'session': session,
        'current_question': current_question,
        'last_answered': last_answered,
        'question_number': answered_questions.count() + 1,
        'total_questions': 5,
        'progress_percentage': (answered_questions.count() / 5) * 100
    }
    return render(request, 'ai_interviewer/interview_session.html', context)

@login_required
def interview_results(request, session_id):
    """Display interview results and analytics"""
    try:
        session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
        answered_questions = session.questions.filter(answer__isnull=False).prefetch_related('answer')
        
        # If no answered questions, return a message
        if not answered_questions.exists():
            return HttpResponse(f"Session {session_id} has no answered questions yet. Complete the interview first.")
        
        # Calculate comprehensive metrics
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
        
        print(f"DEBUG: Rendering results for session {session_id}")
        print(f"DEBUG: Total questions: {total_questions}")
        print(f"DEBUG: Average rating: {average_rating}")
        
        return render(request, 'ai_interviewer/interview_results_simple.html', context)
    except Exception as e:
        print(f"ERROR in interview_results: {e}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error loading results: {e}", status=500)

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