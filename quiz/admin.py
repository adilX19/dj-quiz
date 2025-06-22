from django.contrib import admin
from .models import *

admin.site.register(Subject)
admin.site.register(Answer)
admin.site.register(TakenQuiz)
admin.site.register(StudentAnswer)

class QuizFilter(admin.SimpleListFilter):
  title = 'Quiz'
  parameter_name = 'quiz'

  def lookups(self, request, model_admin):
    quizzes = set([quiz for quiz in Quiz.objects.all()])
    return [(q.id, q.title) for q in quizzes]

  def queryset(self, request, queryset):
    if self.value():
      return queryset.filter(quiz__id__exact=self.value())
    else:
      return queryset

class QuestionInline(admin.StackedInline):
  model = Question
  extra = 5

class AnswerInline(admin.TabularInline):
  model = Answer
  extra = 4

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
  list_display = ['title', 'teacher', 'subject', 'starts_at', 'ends_at']
  inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
  list_display = ['text', 'quiz']
  list_filter = (QuizFilter, 'is_active')
  inlines = [AnswerInline]