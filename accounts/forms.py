from .models import StudentProfile, TeacherProfile, User
from django import forms
from bootstrap_modal_forms.forms import BSModalForm

class SignUpForm(BSModalForm):
	username = forms.CharField(max_length=20)
	gender = forms.ChoiceField(choices=(('M','Male'),('F', 'Female')))
	email = forms.EmailField()
	password = forms.CharField(widget=forms.PasswordInput)
	confirm_password = forms.CharField(widget=forms.PasswordInput)

	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)
		for field_name in self.fields.keys():
			self.fields[field_name].widget.attrs.update({'class': 'form-control'})

	def clean_username(self):
		username = self.cleaned_data.get('username')
		alread_used_usernames = [user.username for user in User.objects.all()]
  
		if username in alread_used_usernames:
			raise forms.ValidationError("Username already in use.")
		return username

	def clean_confirm_password(self):
		passowrd1 = self.cleaned_data.get('password')
		password2 = self.cleaned_data.get('confirm_password')

		if passowrd1 != password2:
			raise forms.ValidationError('Mismatched Password')
		return password2

# REDUNDANT CODE DOWN HERE, NEEDS TO BE OPTIMIZED

class StudentProfileSettingForm(forms.ModelForm):
	username       = forms.CharField(max_length=50)
	first_name     = forms.CharField(max_length=20)
	last_name      = forms.CharField(max_length=20)
	email          = forms.EmailField()
	profile_image  = forms.ImageField(required=False)
	gender         = forms.ChoiceField(widget=forms.Select(), choices=[('M', 'Male'), ('F', 'Female')], required=True)

	def __init__(self, user, *args, **kwargs):
		super(StudentProfileSettingForm, self).__init__(*args, **kwargs)

		# Pre-fill user info
		self.initial['username'] = user.username
		self.initial['first_name'] = user.first_name
		self.initial['last_name'] = user.last_name
		self.initial['email'] = user.email
		self.initial['profile_image'] = user.profile_image
		self.initial['gender'] = user.gender

		# Add Bootstrap classes to each field
		for visible in self.visible_fields():
			if visible.field.widget.__class__.__name__ != "CheckboxInput":
				visible.field.widget.attrs['class'] = 'form-control'
			else:
				visible.field.widget.attrs['class'] = 'form-check-input'

	class Meta:
		model = StudentProfile
		fields = ('username', 'first_name', 'last_name', 'email', 'bio', 'profile_image', 'gender')

class TeacherProfileSettingForm(forms.ModelForm):
	username   = forms.CharField(max_length=50)
	first_name = forms.CharField(max_length=20)
	last_name  = forms.CharField(max_length=20)
	email      = forms.EmailField()
	profile_image = forms.ImageField()
	gender = forms.ChoiceField(widget=forms.Select(), choices=[('M', 'Male'), ('F', 'Female')], required=True)

	def __init__(self, user, *args, **kwargs):
		super(TeacherProfileSettingForm, self).__init__(*args, **kwargs)
		self.initial['username'] = user.username
		self.initial['first_name'] = user.first_name
		self.initial['last_name'] = user.last_name
		self.initial['email'] = user.email
		self.initial['profile_image'] = user.profile_image
		self.initial['gender'] = user.gender

	class Meta:
		model  = TeacherProfile
		fields = ('username', 'first_name', 'last_name', 'email', 'about')
