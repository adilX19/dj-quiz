from django.urls import path
from .views import teacher_views, student_views, classroom_views

# TEACHERS LOGIC PATTERNS
urlpatterns = [
  path('teachers/home/', teacher_views.TeacherQuizHomeView.as_view(), name='teachers_dashboard'),
  path('teachers/quiz/<int:pk>/details/', teacher_views.TeacherQuizDetailView.as_view(), name='quiz_cms_details'),
  path('quiz/create/', teacher_views.QuizCreateUpdateView.as_view(), name='create_quiz'),
  path('quiz/<int:id>/update/', teacher_views.QuizCreateUpdateView.as_view(), name='update_quiz'),
  path('quiz/<int:id>/delete/', teacher_views.QuizDeleteView.as_view(), name='delete_quiz'),
  path('quiz/question/<int:pk>/delete/', teacher_views.QuestionDeleteView.as_view(), name='delete_question'),
  path('quiz/<int:pk>/question/create/', teacher_views.QuestionCreateUpdateView.as_view(), name='create_question'),
  path('quiz/<int:pk>/question/<int:question_id>/update/', teacher_views.QuestionCreateUpdateView.as_view(), name='update_question'),
  path('questions/order/', teacher_views.OrderQuestion.as_view(), name='order_questions'),
  path('quiz/<slug:slug>/results/', teacher_views.QuizResultsView.as_view(), name='quiz_results'),
  path('quiz/<int:quiz_id>/<int:student_id>/export/pdf/', teacher_views.export_quiz_result_pdf, name='export_quiz_result_pdf'),
]

# STUDENTS LOGIC PATTERNS
urlpatterns += [
  path('students/home/', student_views.StudentHomeView.as_view(), name='students_dashboard'),
  path('students/quiz/<int:pk>/details/', student_views.StudentQuizDetailView.as_view(), name='quiz_details'),
  path('students/quiz/<int:quiz_id>/re-attempt/', student_views.StudentReAttemptView.as_view(), name='re_attempt_quiz'),
  path('students/quiz/<int:quiz_id>/question/attempt/', student_views.StudentQuizAttemptView.as_view(), name='attempt_quiz'),
  path('students/classrooms/', classroom_views.StudentClassroomListView.as_view(), name='student_classrooms'),
]

# CLASSROOM LOGIC PATTERNS
urlpatterns += [
  path('classrooms/', classroom_views.ClassroomListView.as_view(), name='classroom_list'),
  path('classrooms/create/', classroom_views.ClassroomCreateView.as_view(), name='classroom_create'),
  path('classrooms/<slug:slug>/join/', classroom_views.JoinClassroomView.as_view(), name='join_classroom'),
  path('classrooms/<slug:slug>/leave/', classroom_views.LeaveClassroomView.as_view(), name='leave_classroom'),
  path('classrooms/<slug:slug>/', classroom_views.ClassroomDetailView.as_view(), name='classroom_detail'),
  path('classrooms/<slug:slug>/edit/', classroom_views.ClassroomUpdateView.as_view(), name='classroom_edit'),
  path('classrooms/<slug:slug>/delete/', classroom_views.ClassroomDeleteView.as_view(), name='classroom_delete'),
]