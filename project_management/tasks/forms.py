from datetime import datetime

from django import forms

from .models import Task, TaskUpdates
from project_management.users.models import User
from project_management.teams.models import TeamMember


class TaskForm(forms.Form):
    task_name = forms.CharField(label='Task Name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Task Name'}))
    assigned_to = forms.ModelChoiceField(
        label='Assign to',
        queryset=User.objects.filter(user_type=User.UserType.MANAGER),
        widget=forms.Select(attrs={'class': 'form-control'})
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
    task_description = forms.CharField(label='Team description', widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    def __init__(self, team, *args, **kwargs):
        super(TaskForm, self).__init__(*args)
        self.fields['assigned_to'].queryset = TeamMember.objects.filter(team=team)

    def save(self, project):
        data = self.cleaned_data
        date_time_now = datetime.now()
        task = Task(task_name=data['task_name'], description=data['task_description'], end_date_time=data['end_date_time'],
                    assigned_to=data['assigned_to'].user, belong_to=project, start_date_time=date_time_now)
        task.save()
        return task

class TaskUpdatesForm(forms.Form):
    update = forms.CharField(
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

    def save(self, task, user):
        data = self.cleaned_data
        updates = TaskUpdates(task=task, user=user, update_description=data['update'])
        updates.save()
        return updates
