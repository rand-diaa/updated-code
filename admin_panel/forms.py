from django import forms
from exam import models

class CourseForm(forms.ModelForm):
    class Meta:
        model=models.Course
        fields=['course_name']

class QuestionForm(forms.ModelForm):
    
    #this will show dropdown __str__ method course model is shown on html so override it
    #to_field_name this will fetch corresponding value  user_id present in course model and return it
    courseID=forms.ModelChoiceField(queryset=models.Course.objects.all(),empty_label="Course Name", to_field_name="id")
    class Meta:
        model=models.Question
        fields=['question_type','marks','question','option1','option2','option3','option4','answer']
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



