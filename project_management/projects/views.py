import pandas as pd

from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, View, TemplateView
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from project_management.utils.permissions import NotEmployeePermissionMixin
from project_management.users.models import User
from project_management.tasks.models import Task
from .forms import ProjectForm, ProjectUpdatesForm
from .models import Project, ProjectUpdates


class ProjectListView(LoginRequiredMixin, ListView):
    template_name = 'home/projects.html'
    login_url = 'users:login'
    model = Project
    context_object_name = 'projects'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.user_type == User.UserType.COMPANY_OWNER or user.user_type == User.UserType.HR:
            queryset = queryset.filter(assigned_to__company=user.company)
        elif user.user_type == User.UserType.MANAGER:
            queryset = queryset.filter(assigned_to__manager=user, assigned_to__company=user.company).distinct()
        elif user.user_type == User.UserType.EMPLOYEE:
            queryset = Project.objects.filter(Q(assigned_to__teammember__user=user) | 
                                              Q(assigned_to__manager=user) &
                                              Q(assigned_to__company=user.company)
                                              ).distinct()
        else:
            queryset = queryset.none()
        return queryset

projects_view = ProjectListView.as_view()


# TODO: check if the user is part of the project before returning the detailed view
class ProjectDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'home/project_detail_page.html'
    login_url = 'users:login'

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs['project_id']
        user = self.request.user
        try:
            project = Project.objects.get(id=project_id)
            tasks = Task.objects.filter(belong_to=project)
            if user.user_type == User.UserType.EMPLOYEE:
                tasks = tasks.filter(assigned_to=user)
            context['tasks'] = tasks
            context['project'] = project
        except Team.DoesNotExist:
            raise Http404("Team does not exist")
        return context

project_details_view = ProjectDetailView.as_view()


class CreateProjectView(LoginRequiredMixin, NotEmployeePermissionMixin, TemplateView):
    form_class = ProjectForm
    template_name = 'home/add_project.html'
    login_url = 'users:login'

    def get(self, request, *args, **kwargs):
        user = request.user
        form = self.form_class(company=user.company)
        return self.render_to_response({'form': form})

    def post(self, request, *args, **kwargs):
        company = request.user.company
        form = self.form_class(company, request.POST)
        print(form.errors)
        if form.is_valid():
            form.save()
            data = {'success': True, 'message': 'Data saved successfully!'}
            return JsonResponse(data)
        return self.render_to_response({'form': form})

create_project_view = CreateProjectView.as_view()


class ProjectDiscussView(LoginRequiredMixin, TemplateView):
    template_name = 'home/project_discussion_page.html'
    login_url = 'users:login'
    form_class = ProjectUpdatesForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs['project_id']
        try:
            form = self.form_class
            project = Project.objects.get(id=project_id)
            updates = ProjectUpdates.objects.filter(project=project)
            context['project'] = project
            context['updates'] = updates
            context['form'] = form
        except Project.DoesNotExist:
            raise Http404("Project does not exist")
        return context

    def post(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, id=project_id)
        user = request.user
        form = ProjectUpdatesForm(request.POST)
        if form.is_valid():
            form.save(project, user)
            form = self.form_class()
            updates = ProjectUpdates.objects.filter(project__id=project_id)
            return self.render_to_response({'form': form, 'updates': updates})
        else:
            return HttpResponseBadRequest('Message error')

project_discuss_view = ProjectDiscussView.as_view()


class ProjectCompletionGraphData(LoginRequiredMixin, View):
    queryset = Project.objects.all()

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        project = self.queryset.get(id=self.kwargs['project_id'])
        project_details = project.get_project_completion_details()
        data = [
            {'label': 'Completed', 'value': project_details["completed_percent"]},
            {'label': 'Pending', 'value': project_details["pending_percent"]}
        ]
        return JsonResponse({"data": data}, safe=False)
    
project_completion_graph_data = ProjectCompletionGraphData.as_view()


class ProjectProgressGraphData(LoginRequiredMixin, View):
    queryset = Project.objects.all()
    
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        project = self.queryset.get(id=self.kwargs['project_id'])
        tasks = Task.objects.filter(belong_to=project)

        # Create a Pandas DataFrame of all the tasks
        task_data = pd.DataFrame(list(tasks.values('start_date_time', 'end_date_time', 'task_status')))

        # Create a new column for the completion date, if the task is completed
        task_data.loc[task_data['task_status'] == 'CMP', 'completion_date'] = task_data['end_date_time']
        task_data['completion_date'] = pd.to_datetime(task_data['completion_date'])
        

        # # Create a date range of five equally spaced dates
        date_range = pd.date_range(start=project.start_date_time, end=project.end_date_time, periods=5)

        # # Group the tasks by the completion date, then count the number of completed tasks
        grouped = task_data.groupby(pd.Grouper(key='completion_date', freq='D'))['task_status'].count()
        print(grouped)
        grouped = grouped.reindex(date_range, method='nearest')

        # # Calculate the percentage of completed tasks for each date
        total_tasks = len(tasks)
        percentages = [round((count / total_tasks) * 100, 2) for count in grouped]

        # Create the JSON data
        data = [{'x': date.strftime('%Y-%m-%d'), 'y': percentage} for date, percentage in zip(date_range, percentages)]

        return JsonResponse({"data": data}, safe=False)
    
project_progress_graph_data = ProjectProgressGraphData.as_view()
