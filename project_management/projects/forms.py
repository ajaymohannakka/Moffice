from django import forms
from django.core.exceptions import ValidationError

from .models import Project, ProjectUpdates
from project_management.teams.models import Team, Role


class ProjectForm(forms.Form):
    project_name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(
            attrs={
                'class': 'form-control', 
                'id': 'exampleInputProject1', 
                'placeholder': 'Enter Project Name'
                }))
    start_date_time = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateInput(
            attrs={
                'class': 'form-control', 
                'id': 'datepicker1', 
                'autocomplete': 'off',
                'placeholder': 'Pick start date'
            }
            )
        )
    end_date_time = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateInput(
            attrs={
                'class': 'form-control', 
                'id': 'datepicker2', 
                'autocomplete': 'off',
                'placeholder': 'Pick end date'
            }
            )
        )
    assign_to_team = forms.ModelChoiceField(
        label='Team',
        queryset=Team.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
        )
    project_description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control', 
                'id': 'exampleFormControlTextarea1', 
                'rows': 3, 
                'placeholder': 'Enter Project description'}))

    def __init__(self, company, *args, **kwargs):
        super(ProjectForm, self).__init__(*args)
        self.fields['assign_to_team'].queryset = Team.objects.filter(company=company)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date_time')
        end_date = cleaned_data.get('end_date_time')
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("Start date cannot be later than end date.")
        return cleaned_data
    
    def save(self):
        data = self.cleaned_data
        project = Project(project_name=data['project_name'], description=data['project_description'], 
                    start_date_time=data['start_date_time'], end_date_time=data['end_date_time'],
                    assigned_to=data['assign_to_team'])
        project.save()
        return project


class ProjectUpdatesForm(forms.Form):
    message = forms.CharField(
        label='Update', 
        max_length=100, 
        widget=forms.TextInput(
            attrs={
                'class': 'form-control', 
                'placeholder': 'Enter Your Message',
                'autocomplete': 'off',
                'id': 'message'
                }
            ))    

    def save(self, project, user):
        data = self.cleaned_data
        update = ProjectUpdates(project=project, user=user, message=data['message'])
        update.save()
        return update
