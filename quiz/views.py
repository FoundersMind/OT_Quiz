from django.shortcuts import render, redirect, get_object_or_404
from .models import Quiz, Question, Option, QuizResult
from .forms import QuizForm, EmailEntryForm
from datetime import datetime
from django.db.models import Sum, Count
from datetime import timedelta
from django.utils import timezone

from django.shortcuts import render
from .models import QuizResult, Quiz, Question
from django.db.models import Sum, Count


def home(request):
    user_email = request.session.get("email")
    name=request.session.get("username")

    # Get user stats if email exists
    user_stats = {
        "quizzes_taken": 0,
        "total_score": 0,
        "rank": "--"
    }

    if user_email:
        # Total quizzes taken and total score
        results = QuizResult.objects.filter(email=user_email)
        user_stats["quizzes_taken"] = results.count()
        user_stats["total_score"] = results.aggregate(total=Sum("score"))['total'] or 0

        # Calculate user rank (based on total score)
        all_users = (
            QuizResult.objects
            .values("email")
            .annotate(total_score=Sum("score"))
            .order_by("-total_score")
        )

        for idx, user in enumerate(all_users, start=1):
            if user['email'] == user_email:
                user_stats["rank"] = idx
                break

    # Featured quiz: latest one with questions
    featured_quiz = Quiz.objects.annotate(q_count=Count("question")).filter(q_count__gt=0).order_by("-id").first()

    # Top 3 users
    top_3_users = (
        QuizResult.objects
        .values("email", "name")
        .annotate(total_score=Sum("score"))
        .order_by("-total_score")[:3]
    )

    context = {
        "user_name": name,
        "user_stats": user_stats,
        "featured_quiz": featured_quiz,
        "top_3_users": top_3_users
    }

    return render(request, "home.html", context)


def upcoming_quizzes(request):
    upcoming = Quiz.objects.filter(start_time__gt=timezone.now()).order_by('start_time')
    return render(request, 'upcoming_quizzes.html', {'upcoming_quizzes': upcoming})
def enter_quiz(request):
    if request.method == 'POST':
        form = EmailEntryForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['name']
            email = form.cleaned_data['email']

            request.session['username'] = username
            request.session['email'] = email

            return redirect('home')
    else:
        # ✅ Render form on GET (e.g. after logout)
        form = EmailEntryForm(initial={
            'name': request.session.get('username', ''),
            'email': request.session.get('email', ''),
        })

    return render(request, 'enter_email.html', {'form': form})




from .models import QuizAccess

from .models import Quiz, QuizAccess
from django.utils import timezone

def quiz_list(request):
    # Only show quizzes whose scheduled time has arrived
    quizzes = Quiz.objects.filter(start_time__lte=timezone.now()).order_by('-start_time')

    email = request.session.get('email')

    # Build quiz access status map
    quiz_access_map = {}
    if email:
        accesses = QuizAccess.objects.filter(email=email)
        quiz_access_map = {access.quiz_id: access for access in accesses}

    return render(request, 'quiz_list.html', {
        'quizzes': quizzes,
        'quiz_access_map': quiz_access_map,
    })
def instructions(request):
    return render(request, 'instructions.html')



# views.py
from django.shortcuts import render, redirect
from .models import Quiz, Question, Option
from .forms import QuizForm
from django.core.paginator import Paginator

from django.template.loader import render_to_string
from django.http import HttpResponse
# def quiz_loading(request, quiz_id):
#     quiz = get_object_or_404(Quiz, id=quiz_id)

#     # Check if user has already entered this quiz
#     if request.session.get(f'quiz_entered_{quiz_id}', False):
#         return redirect('quiz_view', quiz_id=quiz_id, page=1)

#     # Mark quiz as entered
#     request.session[f'quiz_entered_{quiz_id}'] = True

#     return render(request, 'quiz_loader.html', {'quiz': quiz})

def quiz_loading(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    email = request.session.get('email')

    if not email:
        return redirect('enter_quiz')  # fallback if email is not in session

    session_key = f'quiz_entered_{quiz_id}_{email}'
    request.session[f'reset_timer_{quiz.id}_{email}'] = True
    if request.session.get(session_key, False):
        return redirect('quiz_view', quiz_id=quiz_id, page=1)

    request.session[session_key] = True

    return render(request, 'quiz_loader.html', {'quiz': quiz})



from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from .models import Quiz, Question, QuizAccess
from .forms import QuizForm
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Quiz, Question, Option
from .forms import QuizForm

from django.core.paginator import EmptyPage
from django.utils.timezone import now
from django.shortcuts import get_object_or_404, redirect, render
from .models import Quiz, Question, Option, QuizResult, QuizAccess
from django.core.paginator import Paginator
from django.utils.timezone import now

def quiz_view(request, quiz_id, page=1):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = Question.objects.filter(quiz=quiz).order_by('id')
    paginator = Paginator(questions, 1)

    try:
        question = paginator.page(page)
    except:
        return redirect('quiz_view', quiz_id=quiz_id, page=1)

    question_obj = question.object_list[0]

    # Prefill answer from session
    initial_data = {}
    stored_answer = request.session.get(f"answer_q{question_obj.id}")
    if stored_answer:
        initial_data[f"question_{question_obj.id}"] = stored_answer

    form = QuizForm(
        request.POST or None,
        initial=initial_data,
        questions=[question_obj]
    )

    email = request.session.get('email')
    reset_timer = False
    if email:
        reset_timer = request.session.pop(f'reset_timer_{quiz.id}_{email}', False)

    reset_id = str(int(now().timestamp())) if reset_timer else None

    # ✅ Handle auto-submit regardless of form validity
    if request.method == 'POST' and 'auto_submit' in request.POST:
        if email:
            access, _ = QuizAccess.objects.get_or_create(email=email, quiz=quiz)
            access.has_submitted = True
            access.save()

            # Calculate score
            score = 0
            for q in questions:
                user_ans = request.session.get(f"answer_q{q.id}")
                correct = Option.objects.filter(question=q, is_correct=True).first()
                if correct and correct.text == user_ans:
                    score += 1
            try:
                time_taken_secs = int(request.POST.get('time_taken_seconds', quiz.duration_minutes * 60))
            except (TypeError, ValueError):
                time_taken_secs = quiz.duration_minutes * 60

            QuizResult.objects.create(
                email=email,
                name=request.session.get('username', 'Anonymous'), 
                quiz=quiz,
                score=score,
                time_taken=timedelta(seconds=time_taken_secs)
            )

        # Clear session answers
        for q in questions:
            request.session.pop(f"answer_q{q.id}", None)

        return redirect('quiz_result', quiz_id=quiz.id)

    # ✅ Standard flow
    if request.method == 'POST':
        if form.is_valid() or not form.cleaned_data:
            answer = form.cleaned_data.get(f"question_{question_obj.id}")
            if answer:
                request.session[f"answer_q{question_obj.id}"] = answer

            if 'submit' in request.POST:
                if email:
                    access, _ = QuizAccess.objects.get_or_create(email=email, quiz=quiz)
                    access.has_submitted = True
                    access.save()

                    score = 0
                    for q in questions:
                        user_ans = request.session.get(f"answer_q{q.id}")
                        correct = Option.objects.filter(question=q, is_correct=True).first()
                        if correct and correct.text == user_ans:
                            score += 1
                    try:
                        time_taken_secs = int(request.POST.get('time_taken_seconds', quiz.duration_minutes * 60))
                    except (TypeError, ValueError):
                        time_taken_secs = quiz.duration_minutes * 60

                    QuizResult.objects.create(
                        email=email,
                        name=request.session.get('username', 'Anonymous'), 
                        quiz=quiz,
                        score=score,
                        time_taken=timedelta(seconds=time_taken_secs)
                    )

                for q in questions:
                    request.session.pop(f"answer_q{q.id}", None)

                return redirect('quiz_result', quiz_id=quiz.id)

        if 'next' in request.POST and question.has_next():
            return redirect('quiz_view', quiz_id=quiz.id, page=page + 1)
        elif 'previous' in request.POST and question.has_previous():
            return redirect('quiz_view', quiz_id=quiz.id, page=page - 1)

    context = {
        'quiz': quiz,
        'form': form,
        'page': page,
        'num_pages': paginator.num_pages,
        'has_next': question.has_next(),
        'has_previous': question.has_previous(),
        'question_number': question_obj.id,
        'reset_timer': reset_timer,
        'reset_id': reset_id,
    }
    return render(request, 'take_quiz.html', context)



from django.shortcuts import render, get_object_or_404
from .models import Quiz, QuizResult

def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    name = request.session.get('username')   # ✅ use 'username'
    email = request.session.get('email')     # ✅ use 'email'
    result = QuizResult.objects.filter(email=email, quiz=quiz).last()

    return render(request, 'quiz_result.html', {
        'result': result,
        'name': name,
        'quiz': quiz
    })



from django.db.models import Sum, Count
from .models import QuizResult

def leaderboard(request):
    top_users_raw = (
        QuizResult.objects
        .values('email', 'name')  # ✅ include name
        .annotate(total_score=Sum('score'), total_quizzes=Count('quiz'))
        .order_by('-total_score')[:10]
    )

    return render(request, 'leaderboard.html', {'top_users': top_users_raw})


from django.shortcuts import redirect

def quiz_exit(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    email = request.session.get('email')  # ✅ Corrected

    if email:
        access, _ = QuizAccess.objects.get_or_create(email=email, quiz=quiz)
        access.has_exited = True
        access.save()

    return redirect('quiz_list')


from django.shortcuts import render, get_object_or_404
from .models import Quiz, QuizResult

def quiz_leaderboard(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    top_results = (
        QuizResult.objects.filter(quiz=quiz)
        .order_by('-score', 'time_taken')[:3]
    )
    return render(request, 'quiz_leaderboard.html', {
        'quiz': quiz,
        'top_results': top_results,
    })




