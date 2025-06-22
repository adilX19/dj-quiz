from django import template
register = template.Library()

@register.filter()
def already_selected_by(subject, user):
  if subject in user.interests.all():
    return True
  return False

@register.filter()
def already_attempted_quiz_by(quiz, student):
  if student.taken_quizzes.filter(quiz=quiz).exists():
    return True
  return False

@register.filter()
def already_joined_by_student(classroom, student):
  if student.classrooms.filter(id=classroom.id).exists():
    return True
  return False

@register.filter(name='add_class')
def add_class(field, css_class):
  try:
    return field.as_widget(attrs={"class": css_class})
  except AttributeError:
    return field  # fallback for non-field values