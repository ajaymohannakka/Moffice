from datetime import timedelta
import pandas as pd

from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.db.models import OuterRef, Subquery
from django.db.models import Sum, Case, When, BooleanField, FloatField, F

from project_management.utils.permissions import HRLevelPermissionMixin
from project_management.utils.permissions import NotEmployeePermissionMixin
from project_management.users.models import User
from project_management.tasks.models import Task
from project_management.teams.models import TeamMember, Team
from project_management.projects.models import Project
from .models import UserRate
from .utils import format_working_time


class ManageBudgetListView(LoginRequiredMixin, NotEmployeePermissionMixin, TemplateView):
    template_name = 'home/budget_page.html'
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.request.user.company
        users = company.user_set.all()
        data = []
        for user in users:
            user_rates_for_all_projects = UserRate.objects.filter(user=user)
            if len(user_rates_for_all_projects):
                for user_rate in user_rates_for_all_projects:
                    project = user_rate.project
                    progress = user.get_task_stats(project)
                    working_hours = user.get_total_working_hours(project)
                    cost_per_hour = user_rate.user_rate_per_hour
                    total_cost = round(working_hours * cost_per_hour, 2)
                    payment_status = "paid" if project.project_status == Project.ProjectStatus.COMPLETED else "pending"                    
                    if user.user_type == User.UserType.MANAGER:
                        role = 'Manager'
                    else:
                        team = project.assigned_to
                        team_member = TeamMember.objects.filter(team = team, user = user).first()
                        role = team_member.role.role
                    data.append({
                        "name": f"{user.first_name} {user.last_name}",
                        "email": user.email,
                        "role": role,
                        "project": project.project_name,
                        "progress": f"{progress}%",
                        "cost_per_hour": cost_per_hour,
                        "total_cost": total_cost,
                        "status": payment_status
                    })
                    context["result"] = data
        return context

manage_budget_list_view = ManageBudgetListView.as_view()


class UserListView(LoginRequiredMixin, HRLevelPermissionMixin, ListView):
    template_name = 'home/employee_budget_page.html'
    login_url = 'users:login'
    model = User
    context_object_name = 'users'

    def get_queryset(self):
        company = self.request.user.company
        return (super().get_queryset()
        .filter(company=company)
        .exclude(
            Q(user_type=User.UserType.HR) |
            Q(user_type=User.UserType.COMPANY_OWNER)
            ).distinct()
        )

user_list_view = UserListView.as_view()


class UserBudgetView(LoginRequiredMixin, HRLevelPermissionMixin, TemplateView):
    template_name = 'home/project_budget_page.html'
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = kwargs['user_id']
        user_rate_qs = UserRate.objects.filter(
            project=OuterRef('pk'),
            user_id=user_id
        ).order_by('-id')
        context["projects"] = Project.objects.filter(
            Q(assigned_to__teammember__user__id=user_id) | 
            Q(assigned_to__manager__id=user_id)
        ).distinct().annotate(rate=Subquery(user_rate_qs.values('user_rate_per_hour')[:1]))
        return context
    
    def post(self, request, **kwargs):
        cost = request.POST.get('cost')
        project_id = request.POST.get('project_id')
        user_id = kwargs['user_id']
        
        user_rate_obj, created = UserRate.objects.get_or_create(
            project_id=project_id,
            user_id=user_id,
        )
        
        user_rate_obj.user_rate_per_hour = cost
        user_rate_obj.save()
        
        return JsonResponse({'success': True})

user_budget_view = UserBudgetView.as_view()
