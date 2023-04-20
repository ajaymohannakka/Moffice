from django import forms

from .models import Team, TeamMember, Role
from project_management.users.models import User


class TeamForm(forms.Form):
    team_name = forms.CharField(label='Team Name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Team Name'}))
    manager = forms.ModelChoiceField(
        label='Manager',
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
        )
    team_description = forms.CharField(label='Project description', widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    def __init__(self, company, *args, **kwargs):
        super(TeamForm, self).__init__(*args)
        self.company = company
        self.fields['manager'].queryset = User.objects.filter(company=company, user_type=User.UserType.MANAGER)

    def save(self):
        data = self.cleaned_data
        team = Team(team_name=data['team_name'], team_description=data['team_description'], 
                    manager=data['manager'], company=self.company)
        team.save()
        return team


class TeamMemberForm(forms.Form):
    user = forms.ModelChoiceField(
        label='Manager',
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
        )
    role = forms.ModelChoiceField(
        label='Role',
        queryset=Role.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
        )

    def __init__(self, team, *args, **kwargs):
        super(TeamMemberForm, self).__init__(*args)
        self.team = team
        self.fields['user'].queryset = User.objects.filter(company=team.company)
        self.fields['role'].queryset = Role.objects.filter(company=team.company)

    def save(self):
        data = self.cleaned_data
        team_member = TeamMember(team=self.team, user=data['user'], role=data['role'])
        team_member.save()
        return team_member
