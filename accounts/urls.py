from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
  path('login/', views.LoginView.as_view(), name='login'),
  path('logout/', views.LogoutView.as_view(), name='logout'),
  path('password/change/', views.PasswordChangeView.as_view(), name='change_password'),
  path('signup/', views.SignUpSelectionView.as_view(), name='signup'),

  path('student/signup/<str:user_role>/', views.SignUpView.as_view(), name='student_signup'),
  path('teacher/signup/<str:user_role>/', views.SignUpView.as_view(), name='teacher_signup'),
  path('update/', views.ProfileUpdateView.as_view(), name='update_profile'),
  path('student/details/', views.StudentProfileView.as_view(), name='student_profile_details'),
  path('teacher/details/', views.TeacherProfileView.as_view(), name='teacher_profile_details'),
  path('teacher/<int:teacher_id>/details/', views.TeacherProfileView.as_view(), name='teacher_profile_details_for_student'),
]

# Django's built-in auth views patterns 
urlpatterns += [
  path('reset_password/', 
    auth_views.PasswordResetView.as_view(
      template_name='accounts/authentications/reset_password.html'
      ), 
    name='reset_password'),

  path('reset_password_sent/', 
    auth_views.PasswordResetDoneView.as_view(
      template_name='accounts/authentications/password_reset_sent.html'
      ), 
    name='password_reset_done'),

  path('reset/<uidb64>/<token>', 
    auth_views.PasswordResetConfirmView.as_view(
      template_name='accounts/authentications/password_reset_form.html'
      ),
    name='password_reset_confirm'),

  path('reset_password_complete/', 
    auth_views.PasswordResetCompleteView.as_view(
      template_name='accounts/authentications/password_reset_done.html'
      ),
    name='password_reset_complete')
]