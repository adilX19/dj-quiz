from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from ..models import Quiz, Question, Answer, TakenQuiz, StudentAnswer
from ..forms import QuestionForm, QuizForm, AnswersFormSet, AnswerForm

from accounts.models import StudentProfile

class TeacherQuizHomeView(ListView):
  template_name = 'teachers/home.html'
  context_object_name = 'quizzes'
  model = Quiz

  def get_queryset(self):
    qs = super().get_queryset()
    return qs.filter(teacher__user=self.request.user).order_by('-id')

class TeacherQuizDetailView(DetailView):
  model = Quiz
  context_object_name = 'quiz'
  template_name = 'teachers/details.html'

class QuizCreateUpdateView(TemplateResponseMixin, View):
  template_name = 'teachers/create_quiz.html'
  success_url = reverse_lazy('teachers_dashboard')

  def dispatch(self, request, id=None, *args, **kwargs):
    self.quiz_obj = None
    if id:
      self.quiz_obj = get_object_or_404(Quiz, id=id, teacher__user=request.user)
    return super().dispatch(request, id=id, *args, **kwargs)

  def get_form(self, request):
    return QuizForm(
      instance=self.quiz_obj,
      data=request.POST or None,
      teacher=request.user.teacher_profile
    )

  def get(self, request, id=None, *args, **kwargs):
    form = self.get_form(request)
    return self.render_to_response({'form': form, 'object': self.quiz_obj})

  def post(self, request, id=None, *args, **kwargs):
    form = self.get_form(request)
    if form.is_valid():
      quiz = form.save(commit=False)
      quiz.teacher = request.user.teacher_profile
      quiz.save()
      return HttpResponseRedirect(self.success_url)
    return self.render_to_response({'form': form, 'object': self.quiz_obj})

class QuizDeleteView(View):
  def get(self, request, id, *args, **kwargs):
    quiz = get_object_or_404(Quiz, id=id, teacher__user=request.user)
    quiz.delete()
    return redirect('teachers_dashboard')

class QuestionCreateUpdateView(CreateView):
  template_name = 'teachers/create_question.html'
  model = Question
  quiz = None
  question = None

  def __init__(self):
    self.success_url = None

  def dispatch(self, request, pk, question_id=None, *args, **kwargs):
    self.quiz = get_object_or_404(Quiz, id=pk, teacher__user=request.user)
    self.success_url = reverse_lazy('quiz_cms_details', kwargs={'pk': self.quiz.id})

    if question_id:
      self.question = get_object_or_404(Question, id=question_id, quiz=self.quiz)
    return super(QuestionCreateUpdateView, self).dispatch(request, pk, *args, **kwargs)

  def get(self, request, pk, *args, **kwargs):
    self.object = None
    form = QuestionForm(request.POST or None, instance=self.question)
    answer_forms = AnswersFormSet(instance=self.question, data=None)

    existing = answer_forms.total_form_count()
    if existing < 4:
        AnswerFormSetFactory = inlineformset_factory(
            Question,
            Answer,
            form=AnswerForm,
            fields=['text', 'is_correct'],
            extra=(4 - existing),
            max_num=4,
            can_delete=True
        )
        answer_forms = AnswerFormSetFactory(instance=self.question)

    return self.render_to_response(
      self.get_context_data(
        form=form, answer_forms=answer_forms
      )
    )

  def post(self, request, pk, *args, **kwargs):
    self.object = None
    form = QuestionForm(request.POST, instance=self.question)
    answer_forms = AnswersFormSet(instance=self.question, data=self.request.POST)

    print(self.request.POST)
    answers = {i: self.request.POST.get(f"answers-{i}-text")  for i in range(0, 4)}
    correct_answer = None

    for _ in range(0, 4):
      if self.request.POST.get(f"answers-{_}-is_correct", False):
        correct_answer = _
        break

    self.question.answers.update(is_correct=False)
    self.question.answers.filter(text=answers[correct_answer]).update(is_correct=True)

    return self.form_valid(form, answer_forms)

  def form_valid(self, form, answer_forms):

    if self.question:
      form.save()
      answer_forms.instance = self.question
      answer_forms.save()
    else:
      question = form.save(commit=False)
      question.quiz = self.quiz
      question.save()
      self.object = question
      answer_forms.instance = self.object
      answer_forms.save()

    return redirect('quiz_cms_details', pk=self.quiz.id)

  def form_invalid(self, form, answer_forms):
    return self.render_to_response(
      self.get_context_data(
        form=form, answer_forms=answer_forms
      )
    )

class QuestionDeleteView(View):
  def get(self, request, pk, *args, **kwargs):
    question = get_object_or_404(Question, id=pk, quiz__teacher__user=request.user)
    question.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class QuizResultsView(DetailView):
  model = Quiz
  template_name = 'teachers/quiz_results.html'
  context_object_name = 'quiz'
  slug_url_kwarg = 'slug'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    quiz = self.get_object()
    taken_quizzes = TakenQuiz.objects.filter(quiz=quiz).select_related('student__user')

    context['taken_quizzes'] = taken_quizzes
    return context

class OrderQuestion(CsrfExemptMixin, JsonRequestResponseMixin, View):
  def post(self, request, *args, **kwargs):
    for object_id, order in self.request_json.items():
      print(type(object_id), object_id)
      Question.objects.filter(
        id=int(object_id),
        quiz__teacher__user=request.user
      ).update(order=order)
    return self.render_json_response({'message': 'Reordered successfully'})

from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse

def render_to_pdf(template_src, context_dict={}):
  template = get_template(template_src)
  html  = template.render(context_dict)
  response = HttpResponse(content_type='application/pdf')
  pisa_status = pisa.CreatePDF(html, dest=response)
  if pisa_status.err:
    return HttpResponse('We had some errors <pre>' + html + '</pre>')
  return response

def export_quiz_result_pdf(request, quiz_id, student_id):
  quiz = Quiz.objects.get(id=quiz_id)
  student = StudentProfile.objects.get(id=int(student_id))
  taken_quiz = TakenQuiz.objects.get(student=student, quiz=quiz)

  # Map each answer to its question
  student_answers = StudentAnswer.objects.filter(student=student, answer__question__quiz=quiz).select_related('answer', 'answer__question')

  context = {
    'quiz': quiz,
    'student': student,
    'taken_quiz': taken_quiz,
    'answers': student_answers,
    'total_marks': sum(q.score or 1 for q in quiz.questions.all())
  }

  return render_to_pdf('teachers/pdf_result.html', context)