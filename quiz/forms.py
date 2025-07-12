from django import forms
from django.core.exceptions import ValidationError
from .models import Question, Option

# forms.py
class QuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.question_data = []  # for manual rendering
        questions = kwargs.pop('questions')
        super().__init__(*args, **kwargs)
        for question in questions:
            options = Option.objects.filter(question=question)
            field_name = f"question_{question.id}"
            self.fields[field_name] = forms.ChoiceField(
                choices=[(opt.text, opt.text) for opt in options],
                required=True,
                widget=forms.HiddenInput()  # Hide Django’s field rendering
            )
            self.question_data.append({
                "field_name": field_name,
                "question": question,
                "options": options
            })


# 🔹 Email Entry Form with Default + Validation
class EmailEntryForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'class': 'form-control text-dark bg-white'
        })
    )

    email = forms.EmailField(
        initial="abc@opentext.com",
        widget=forms.EmailInput(attrs={
            'placeholder': 'you@opentext.com',
            'class': 'form-control text-dark bg-white'
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email.lower().endswith('@opentext.com'):
            raise ValidationError("Only @opentext.com email addresses are allowed.")
        return email
