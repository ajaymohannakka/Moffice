from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.http import JsonResponse

from .forms import TeamForm, TeamMemberForm
from .models import Team, TeamMember
from project_management.utils.permissions import NotEmployeePermissionMixin
from project_management.users.models import User


class TeamListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = 'home/teams.html'
    login_url = 'users:login'
    context_object_name = 'teams'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.user_type == User.UserType.COMPANY_OWNER or user.user_type == User.UserType.HR:
            queryset = queryset.filter(company=user.company)
        elif user.user_type == User.UserType.MANAGER:
            queryset = queryset.filter(manager=user)
        elif user.user_type == User.UserType.EMPLOYEE:
            queryset = queryset.filter(teammember__user=user)
        else:
            queryset = queryset.none()
        return queryset

teams_view = TeamListView.as_view()


class DetailsTeamView(LoginRequiredMixin, TemplateView):
    template_name = 'home/team_detail_page.html'
    login_url = 'users:login'
    form_class = TeamMemberForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team_id = self.kwargs['team_id']
        try:
            team = Team.objects.get(id=team_id)
            form = self.form_class(team=team)
            context['team'] = team
            context['members'] = team.teammember.all()
            context['form'] = form
        except Team.DoesNotExist:
            raise Http404("Team does not exist")
        return context

    def post(self, request, *arg, **kwargs):
        team_id = self.kwargs['team_id']
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise e
        form = self.form_class(team, request.POST)
        if form.is_valid():
            form.save()
            data = {'success': True, 'message': 'Data saved successfully!'}
            return JsonResponse(data)
        return self.render_to_response({'form': form})

details_team_view = DetailsTeamView.as_view()


class CreateTeamView(LoginRequiredMixin, NotEmployeePermissionMixin, TemplateView):
    template_name = 'home/add_team.html'
    login_url = 'users:login'
    form_class = TeamForm

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.user.company)
        return self.render_to_response({'form': form})

    def post(self, request, *args, **kwargs):
        company = request.user.company
        form = TeamForm(company, request.POST)
        if form.is_valid():
            form.save()
            data = {'success': True, 'message': 'Data saved successfully!'}
            return JsonResponse(data)
        return self.render_to_response({'form': form})

create_team_view = CreateTeamView.as_view()
