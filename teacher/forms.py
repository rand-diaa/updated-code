from django import forms
from django.contrib.auth.models import User
from . import models
from exam import models as EXAM

class TeacherUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }

class TeacherForm(forms.ModelForm):
    class Meta:
        model=models.Teacher
        fields=['email','mobile','profile_pic']


class ExamBundleForm(forms.ModelForm):
    class Meta:
        model = EXAM.ExamBundle
        fields = ['title', 'course', 'duration_minutes', 'per_question_seconds']


class TeacherQuestionForm(forms.ModelForm):
    class Meta:
        model = EXAM.Question
        fields = ['question_type', 'marks', 'question', 'option1', 'option2', 'option3', 'option4', 'answer']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3, 'cols': 50})
        }

    def clean(self):
        cleaned_data = super().clean()
        question_type = cleaned_data.get('question_type')
        if question_type == 'tf':
            cleaned_data['option1'] = 'True'
            cleaned_data['option2'] = 'False'
            cleaned_data['option3'] = ''
            cleaned_data['option4'] = ''
            if cleaned_data.get('answer') not in ['True', 'False']:
                self.add_error('answer', 'Select True or False for this question type.')
        else:
            for field_name in ['option1', 'option2', 'option3', 'option4']:
                if not cleaned_data.get(field_name):
                    self.add_error(field_name, 'This field is required for multiple choice questions.')
        return cleaned_data

