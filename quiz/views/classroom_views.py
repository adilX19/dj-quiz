from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views.generic.base import View, TemplateResponseMixin
from django.shortcuts import get_object_or_404, redirect
from ..models import Classroom
from ..forms import ClassroomForm, JoinClassroomForm

# Teacher must be logged in
from django.contrib.auth.mixins import LoginRequiredMixin

class ClassroomListView(LoginRequiredMixin, ListView):
    model = Classroom
    template_name = 'classroom/list.html'

    def get_queryset(self):
        return Classroom.objects.filter(teacher=self.request.user.teacher_profile)

class ClassroomDetailView(LoginRequiredMixin, DetailView):
    model = Classroom
    template_name = 'classroom/detail.html'

class ClassroomCreateView(LoginRequiredMixin, CreateView):
    model = Classroom
    form_class = ClassroomForm
    template_name = 'classroom/form.html'
    success_url = reverse_lazy('classroom_list')

    def form_valid(self, form):
        form.instance.teacher = self.request.user.teacher_profile
        return super().form_valid(form)

class ClassroomUpdateView(LoginRequiredMixin, UpdateView):
    model = Classroom
    form_class = ClassroomForm
    template_name = 'classroom/form.html'
    success_url = reverse_lazy('classroom_list')

class ClassroomDeleteView(LoginRequiredMixin, DeleteView):
    model = Classroom
    template_name = 'classroom/confirm_delete.html'
    success_url = reverse_lazy('classroom_list')

# student views
class StudentClassroomListView(LoginRequiredMixin, ListView):
    model = Classroom
    template_name = 'classroom/list.html'

    def get_queryset(self):
        return self.request.user.student_profile.classrooms.all()


class JoinClassroomView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        classroom = get_object_or_404(Classroom, slug=slug)

        student_profile = request.user.student_profile
        if not classroom.students.filter(id=student_profile.id).exists():
            classroom.students.add(student_profile)

        return redirect(f"http://127.0.0.1:8000/quizzes/classrooms/{classroom.slug}/")


class LeaveClassroomView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        classroom = get_object_or_404(Classroom, slug=slug)

        student_profile = request.user.student_profile
        if classroom.students.filter(id=student_profile.id).exists():
            classroom.students.remove(student_profile)

        return redirect('students_dashboard')