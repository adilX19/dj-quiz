from django import forms
from django.forms.models import inlineformset_factory
from .models import Question, Answer, Quiz, Classroom

class JoinClassroomForm(forms.Form):
  slug = forms.CharField(label="Classroom Code or Slug", max_length=100)

class ClassroomForm(forms.ModelForm):
  class Meta:
    model = Classroom
    fields = ['name', 'students']
    widgets = {
      'name': forms.TextInput(attrs={'class': 'form-control'}),
      'students': forms.SelectMultiple(attrs={'class': 'form-control'}),
    }


class QuizForm(forms.ModelForm):
  class Meta:
    model = Quiz
    fields = [
      'title', 'summary', 'subject', 'score',
      'starts_at', 'ends_at', 'is_public', 'classroom'
    ]
    widgets = {
      'title': forms.TextInput(attrs={'class': 'form-control'}),
      'summary': forms.Textarea(attrs={'class': 'form-control'}),
      'subject': forms.Select(attrs={'class': 'form-select'}),
      'score': forms.NumberInput(attrs={'class': 'form-control'}),
      'starts_at': forms.TextInput(attrs={'class': 'form-control datetimepicker'}),
      'ends_at': forms.TextInput(attrs={'class': 'form-control datetimepicker'}),
      'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
      'classroom': forms.Select(attrs={'class': 'form-select'}),
    }

  def __init__(self, *args, **kwargs):
    teacher = kwargs.pop('teacher', None)
    super().__init__(*args, **kwargs)
    if teacher:
      self.fields['classroom'].queryset = teacher.classrooms.all()

class QuestionForm(forms.ModelForm):
  class Meta:
    model = Question
    fields = ['text', 'score']
    widgets = {
      'text': forms.Textarea(attrs={
        'class': 'form-control w-50 mx-auto', 
        'placeholder': 'Add new Question here...',
        'rows': "5",
        'cols': "40"
      }),
      'score': forms.TextInput(attrs={'class': 'form-control w-50 mx-auto', 'placeholder': 'Add Score here...'})
    }

class AnswerForm(forms.ModelForm):
  is_correct = forms.BooleanField(required=False)

  class Meta:
      model = Answer
      fields = ['text', 'is_correct']

  def clean(self):
    super().clean()
    correct_answers = sum(
        1 for form in self.forms
        if form.cleaned_data.get('is_correct') and not form.cleaned_data.get('DELETE', False)
    )
    if correct_answers != 1:
        raise forms.ValidationError("Exactly one answer must be marked as correct.")

AnswersFormSet = inlineformset_factory(Question, Answer, fields=['text', 'is_correct'], extra=4)