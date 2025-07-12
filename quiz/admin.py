import nested_admin
from django.contrib import admin
from .models import Quiz, Question, Option, QuizResult, QuizAccess


class OptionInline(nested_admin.NestedTabularInline):
    model = Option
    extra = 2


class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    extra = 1
    inlines = [OptionInline]


@admin.action(description="Allow users to retake selected quizzes")
def reopen_quizzes(modeladmin, request, queryset):
    for quiz in queryset:
        quiz.is_locked = False
        quiz.save()
        QuizAccess.objects.filter(quiz=quiz).delete()

from django.contrib import admin
from .models import UpcomingQuiz

@admin.register(UpcomingQuiz)
class UpcomingQuizAdmin(admin.ModelAdmin):
    list_display = ("title", "scheduled_date", "duration_minutes")
    list_filter = ("scheduled_date",)
    search_fields = ("title", "description")

@admin.register(Quiz)
class QuizAdmin(nested_admin.NestedModelAdmin):
    list_display = ['title', 'duration_minutes', 'created_at', 'show_leaderboard','is_featured','start_time']  # 👈 added
    list_editable = ['show_leaderboard','is_featured','start_time']  # 👈 allows inline toggle
    inlines = [QuestionInline]
    actions = [reopen_quizzes]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'position', 'text']
    list_filter = ['quiz']
    ordering = ['quiz', 'position']


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ['text', 'question']


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ['email', 'quiz', 'score', 'time_taken', 'submitted_at']
    list_filter = ['quiz', 'submitted_at']
    search_fields = ['email', 'quiz__title']


@admin.register(QuizAccess)
class QuizAccessAdmin(admin.ModelAdmin):
    list_display = ['email', 'quiz', 'has_exited', 'has_submitted']
    list_filter = ['quiz', 'has_exited']
    search_fields = ['email']
