from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

from .models import User, Company


class LoginForm(forms.Form):
    email = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
                }
            ),
        required=True
        )
    user_type = forms.ChoiceField(
        choices=User.UserType.choices,
        widget=forms.Select(
            attrs={
                'class': 'form-control', 
                'id': 'group-select'
                }
            ),
        required=True
        )
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-control', 
                'id': 'group-select'
                }
            ),
        required=True
        )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
                }
            ),
            required=True
        )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control"
                }
            ),
            required=True
        )

    class Meta:
        model = User
        fields = ('email', 'company', 'user_type', 'password1', 'password2')


class CreateCompanyForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = ['company_name']
        widgets = {
            'company_name': forms.TextInput(
            attrs={
                "placeholder": "Company Name",
                "class": "form-control"
                }
            )
        }
