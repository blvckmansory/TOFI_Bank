# forms.py
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Users, Documents
from django import forms

User = get_user_model()


class UserCreationForm(UserCreationForm):
    email = forms.EmailField(label="Email", max_length=254, help_text="Enter a valid email address.")
    surname = forms.CharField(max_length=30, required=True, help_text="Enter your surname.")
    patronymic = forms.CharField(max_length=30, required=False, help_text="Enter your patronymic.")

    # Новые поля для документов
    document_type = forms.ChoiceField(choices=Documents.Documents_TYPES)
    document_number = forms.CharField(max_length=16, required=True, help_text="Enter document number")
    identification_number = forms.CharField(max_length=20, required=True, help_text="Enter identification number")
    expiry_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), required=True,
                                  help_text="Enter expiry date")
    date_of_birth = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), required=True,
                                    help_text="Enter date of birth")
    issued_by = forms.CharField(max_length=100, required=True, help_text="Enter issued by")
    issuing_authority_code = forms.CharField(max_length=10, required=True, help_text="Enter issuing authority code")
    place_of_birth = forms.CharField(max_length=100, required=True, help_text="Enter place of birth")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'surname', 'patronymic')


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Users
        fields = ['email', 'username', 'password']


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


