from django.urls import path
from . import views

from django.urls import path
from . import views

from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
   path('', views.enter_quiz, name='enter_quiz'),  # Default landing page (after logout)
path('home/', views.home, name='home'),         # Optional: Home dashboard after login

    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/page/<int:page>/', views.quiz_view, name='quiz_view'),
    path('quiz/<int:quiz_id>/result/', views.quiz_result, name='quiz_result'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('upcoming/', views.upcoming_quizzes, name='upcoming_quizzes'),
    path('instructions/', views.instructions, name='instructions'),

    path('quiz/<int:quiz_id>/loading/', views.quiz_loading, name='quiz_loading'),
    path('quiz/<int:quiz_id>/exit/', views.quiz_exit, name='quiz_exit'),
    path('logout/', LogoutView.as_view(next_page='enter_quiz'), name='logout'),
    path('quiz/<int:quiz_id>/leaderboard/', views.quiz_leaderboard, name='quiz_leaderboard'),


   
]
