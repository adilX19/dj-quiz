from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.base import View, TemplateResponseMixin
from django.contrib import messages
from quiz.models import *

from ..models import Classroom

class StudentHomeView(TemplateResponseMixin, View):
  template_name = 'students/home.html'
  interest_subjects = None
  subjects = None
  
  def dispatch(self, request, *args, **kwargs):
    self.interest_subjects = request.user.student_profile.interests
    if not self.interest_subjects.all():
      self.subjects = Subject.objects.all()
    return super(StudentHomeView, self).dispatch(request, *args, **kwargs)

  def get(self, request, *args, **kwargs):

    taken_quizzes = [tq.quiz.id for tq in request.user.student_profile.taken_quizzes.all()]
    joined_classrooms = [jc.id for jc in request.user.student_profile.classrooms.all()]
    interest_subjects = list(request.user.student_profile.interests.values_list('id', flat=True))

    print(interest_subjects)

    public_quizzes = Quiz.objects.filter(is_public=True, subject__id__in=interest_subjects).order_by('-id').exclude(id__in=taken_quizzes)

    classrooms = Classroom.objects.order_by('-id').exclude(id__in=joined_classrooms)
    classroom_quizzes = Quiz.objects.filter(classroom__in=request.user.student_profile.classrooms.all())

    return self.render_to_response({'subjects': self.subjects, 'public_quizzes': public_quizzes, 'classroom_quizzes': classroom_quizzes, 'classrooms': classrooms})

  def post(self, request, *args, **kwargs):
    selected_subjects_slugs = [slug for slug in list(request.POST.values())[1:]]
    if selected_subjects_slugs and self.subjects:
      for subject_slug in selected_subjects_slugs:
        subject = self.subjects.get(slug=subject_slug)
        if subject not in self.interest_subjects.all():
          self.interest_subjects.add(subject)        
    return self.render_to_response({'message': 'Subjects Selected successfullyy', 'reload': True})

class StudentQuizDetailView(TemplateResponseMixin, View):
  template_name = 'students/details.html'
  obtained_marks = None

  def get(self, request, pk, *args, **kwargs):
    quiz        = get_object_or_404(Quiz, id=pk)
    total_marks = sum([question.score for question in quiz.questions.all() if question and question.score])
    student     = request.user.student_profile
    
    if student.taken_quizzes.filter(quiz=quiz).exists():
        self.obtained_marks = student.taken_quizzes.get(quiz=quiz).obtained_marks

    related_quizzes = Quiz.objects.filter(subject=quiz.subject).exclude(title=quiz.title).order_by('-date_created')[:5]

    return self.render_to_response({
      'quiz': quiz, 
      'obtained_marks': self.obtained_marks, 
      'total_marks':total_marks,
      'related_quizzes': related_quizzes
    })

class StudentQuizAttemptView(TemplateResponseMixin, View):
  template_name        = 'students/quiz_attempt_modal.html'
  quiz                 = None
  student              = None
  unanswered_questions = None

  def dispatch(self, request, quiz_id, *args, **kwargs):
    self.quiz                 = get_object_or_404(Quiz, id=quiz_id)
    self.student              = request.user.student_profile
    self.unanswered_questions = self.student.get_unanswered_questions(self.quiz)
    return super(StudentQuizAttemptView, self).dispatch(request, quiz_id, *args, **kwargs)

  def get(self, request, quiz_id, *args, **kwargs):

    if self.student.taken_quizzes.filter(quiz=self.quiz).exists():
      return redirect('quiz_details', self.quiz.id)
    question = self.unanswered_questions.first()

    return self.render_to_response({
      'question': question, 
      'quiz': self.quiz, 
      'total_questions': self.quiz.questions.count()
    })

  def post(self, request, quiz_id, *args, **kwargs):
    id     = list(request.POST.values())[1:][0]
    answer = get_object_or_404(Answer, id=id, question__quiz=self.quiz)
    StudentAnswer.objects.create(student=self.student, answer=answer)

    if self.student.get_unanswered_questions(self.quiz).exists():
      print("Redirecting to same page")
      return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    correct_answers = self.student.quiz_answers.filter(answer__question__quiz=self.quiz, answer__is_correct=True)

    obtained_marks = sum([correct_answer.answer.question.score for correct_answer in correct_answers])
    total_marks    = sum([question.score for question in self.quiz.questions.all() if question and question.score])
    percentage_is_above_70 = (obtained_marks / total_marks) * 100 > 70.0

    TakenQuiz.objects.create(
      student=self.student,
      quiz=self.quiz,
      obtained_marks=obtained_marks
    )

    if percentage_is_above_70:
      messages.success(request, f'Congratulations! You have got such an amazing marks {obtained_marks} out of {total_marks}')
    else:
      messages.warning(request, f'Fair! You have to work hard {obtained_marks} out of {total_marks}')
    return redirect('quiz_details', self.quiz.id)



class StudentReAttemptView(View):
  def get(self, request, quiz_id, *args, **kwargs):
    student = request.user.student_profile
    quiz = get_object_or_404(Quiz, id=quiz_id)

    TakenQuiz.objects.get(student=student, quiz=quiz).delete()
    [quiz_answer.delete() for quiz_answer in student.quiz_answers.filter(answer__question__quiz=quiz, student=student)]
    return redirect('attempt_quiz', quiz.id)