from django import forms
from .models import UploadedFile, User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ('file',)
class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    class Meta:
        fields = ['username', 'password']