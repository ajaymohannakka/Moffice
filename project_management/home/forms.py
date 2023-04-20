from django import forms

from project_management.users.models import User
from project_management.teams.models import Role


class UserProfileForm(forms.Form):
    first_name = forms.CharField(
        label='First Name',
        max_length=100,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter First Name', 'id': "fn"}
            ))
    last_name = forms.CharField(
        label='Last Name', 
        max_length=100, 
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter Last Name', 'id': "fn"}
            ),
        required=False
        )
    bio = forms.CharField(
        label='Bio', 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'id': "abt" }
        ),
        required=False
    )

    def save(self, user):
        data = self.cleaned_data
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.bio = data['bio']
        user.save()
        return user


class AddRoleForm(forms.Form):
    role = forms.CharField(
        label='Role Name', 
        max_length=100,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter Role'}
            ))

    def save(self, company):
        data = self.cleaned_data
        task = Role(role=data['role'], company=company)
        task.save()
        return task