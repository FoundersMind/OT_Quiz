from django.db import models
from django.utils import timezone
# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_locked = models.BooleanField(default=False)  # ✅ Add this field
    duration_minutes = models.PositiveIntegerField(default=10)
    show_leaderboard = models.BooleanField(default=True)  # 👈 Add this
    is_featured = models.BooleanField(default=False) 
    start_time = models.DateTimeField(default=timezone.now)
    def save(self, *args, **kwargs):
        if self.is_featured:
            Quiz.objects.filter(is_featured=True).update(is_featured=False)
        super().save(*args, **kwargs)

    def is_upcoming(self):
        return self.start_time and self.start_time > timezone.now()

    def is_available(self):
        return not self.start_time or self.start_time <= timezone.now()
    def __str__(self):
        return self.title
# models.py
class QuizAccess(models.Model):
    email = models.EmailField()
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    has_exited = models.BooleanField(default=False)
    has_submitted = models.BooleanField(default=False)  # ✅ New field

    def is_locked(self):
        return self.has_exited or self.has_submitted

    def __str__(self):
        status = "Exited" if self.has_exited else "Submitted" if self.has_submitted else "Active"
        return f"{self.email} - {self.quiz.title} ({status})"

from django.db import models

class UpcomingQuiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    scheduled_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['scheduled_date']

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.TextField()
    position = models.PositiveIntegerField(default=0)  # 👈 Add this

    class Meta:
        ordering = ['position']  # Always order by position

    def __str__(self):
        return f"Q{self.position}: {self.text[:50]}"  # Show position in admin


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)  # ✅ Tick for correct

    def __str__(self):
        return f"{self.text} {'✅' if self.is_correct else ''}"

class QuizResult(models.Model):
    email = models.EmailField(default="abc@opentext.com")
    name = models.CharField(max_length=100,default="opentext")  # ✅ Add this
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    time_taken = models.DurationField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    has_exited = models.BooleanField(default=False)  # ✅ New field

    def __str__(self):
        return f"{self.email} - {self.quiz.title} - {self.score}"


