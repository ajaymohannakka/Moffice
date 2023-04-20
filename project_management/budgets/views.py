from datetime import timedelta
import pandas as pd

from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.db.models import OuterRef, Subquery

from project_management.utils.permissions import HRLevelPermissionMixin
from project_management.utils.permissions import NotEmployeePermissionMixin
from project_management.users.models import User
from project_management.tasks.models import Task
from project_management.projects.models import Project
from .models import UserRate
from .utils import format_working_time


class ManageBudgetListView(LoginRequiredMixin, NotEmployeePermissionMixin, TemplateView):
    template_name = 'home/budget_page.html'
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.request.user.company
        user = self.request.user
        try:
            user_queryset = User.objects.filter(company=company)
            user_data = user_queryset.values(
                'id', 'first_name', 'last_name', 'email',
                'task__start_date_time', 'task__end_date_time',
                'userrate__user_rate_per_hour',
                'task__belong_to__id', 'task__task_status'
            )
            df = pd.DataFrame.from_records(user_data)
            
            df['task__start_date_time'] = pd.to_datetime(df['task__start_date_time'])
            df['task__end_date_time'] = pd.to_datetime(df['task__end_date_time'])
            
            completed_tasks = df['task__task_status'] == Task.TaskStatus.COMPLETED
            df = df[completed_tasks].assign(
                total_working_time=(df['task__end_date_time'] - df['task__start_date_time']).dt.total_seconds()
            )

            df['total_cost'] = df['userrate__user_rate_per_hour'].fillna(0) * df['total_working_time']/3600

            df['total_completed_tasks'] = completed_tasks.astype(int)

            grouped = df.groupby(['id', 'first_name', 'last_name', 'email', 'task__belong_to__id']).agg({
                'total_working_time': 'mean',
                'total_cost': 'sum',
                'total_completed_tasks': 'sum'
            }).reset_index()

            grouped['avg_cost_per_project'] = grouped['total_cost'] / grouped['task__belong_to__id']
            grouped['efficiency'] = (grouped['total_completed_tasks'] / grouped['total_working_time'] * grouped['avg_cost_per_project']) * 100
            grouped['total_working_time'] = grouped['total_working_time'].apply(lambda x: str(timedelta(seconds=x)))

            grouped = grouped.round(0)

            result = grouped[['first_name', 'email', 'total_working_time', 'avg_cost_per_project', 'efficiency']].to_dict('records')
            context['result'] = result
            context['format_working_time'] = format_working_time
        except User.DoesNotExist:
            raise Http404("Team does not exist")
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
