from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from quiz.models import Subject, Quiz

class User(AbstractUser):
  USER_CHOICES = (
    ('S', 'STUDENT'),
    ('T', 'TEACHER'),
  )

  GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
  )

  user_role = models.CharField(max_length=15, choices=USER_CHOICES)
  gender    = models.CharField(max_length=10, choices=GENDER_CHOICES, default='M')
  profile_image  = models.ImageField(upload_to='profile_images/teachers_profile_images/', null=True, blank=True, default='utility_images/default_image.png')

  def save(self, *args, **kwargs):
    created = self.id is None
    super(User, self).save(*args, **kwargs)
    if created and self.user_role == 'T':
      self.groups.add(Group.objects.get(name="Teacher"))
    elif created and self.user_role == 'S':
      self.groups.add(Group.objects.get(name="Student"))

  @property
  def full_name(self):
    return f"{self.first_name} {self.last_name}"

class TeacherProfile(models.Model):
  user           = models.OneToOneField(User, related_name='teacher_profile', on_delete=models.CASCADE)
  place_of_birth = models.CharField(max_length=30, null=True, blank=True)
  about             = models.TextField(null=True, blank=True)
  facebook_profile  = models.URLField(null=True, blank=True)
  twitter_profile   = models.URLField(null=True, blank=True)
  github_profile    = models.URLField(null=True, blank=True)
  instagram_profile = models.URLField(null=True, blank=True)

  def __str__(self):
    return f"{self.user.full_name}"

class StudentProfile(models.Model):
  user          = models.OneToOneField(User, related_name='student_profile', on_delete=models.CASCADE)
  interests     = models.ManyToManyField(Subject, blank=True)
  bio           = models.TextField(null=True, blank=True)

  def get_unanswered_questions(self, quiz):
    answered_question = self.quiz_answers.filter(answer__question__quiz=quiz).values_list('answer__question__pk', flat=True)
    questions = quiz.questions.exclude(pk__in=answered_question)
    return questions

  def __str__(self):
    return f"{self.user.full_name}"