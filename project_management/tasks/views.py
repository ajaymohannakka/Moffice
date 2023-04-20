import json
from datetime import datetime

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import QueryDict
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.views.generic import ListView
from django.views import View
from django.http import JsonResponse

from project_management.utils.permissions import NotEmployeePermissionMixin
from project_management.users.models import User
from project_management.projects.models import Project
from .forms import TaskForm, TaskUpdatesForm
from .models import Task, TaskUpdates


class CreateTaskView(LoginRequiredMixin, NotEmployeePermissionMixin, TemplateView):
    template_name = 'home/add_task.html'
    login_url = 'users:login'
    form_class = TaskForm

    def get(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        try:
            project = Project.objects.get(id=project_id)
            team = project.assigned_to
        except:
            raise e
        form = self.form_class(team=team)
        return self.render_to_response({'form': form})

    def post(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        try:
            project = Project.objects.get(id=project_id)
            team = project.assigned_to
        except:
            raise e
        form = TaskForm(team, request.POST)
        if form.is_valid():
            form.save(project)
            data = {'success': True, 'message': 'Data saved successfully!'}
            return JsonResponse(data)
        return self.render_to_response({'form': form})

create_task_view = CreateTaskView.as_view()


class TaskStatusUpdateView(LoginRequiredMixin, View):
    def patch(self, request, *args, **kwargs):
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, id=task_id)
        request_body = request.body.decode('utf-8')
        post_data = QueryDict(request_body)

        task_status = post_data.get('task_status')

        if task_status:
            task.task_status = task_status
            if task_status == Task.TaskStatus.COMPLETED:
                task.end_date_time = datetime.now()
            task.save()
            return JsonResponse({'message': 'Task status updated successfully'})
        else:
            return HttpResponseBadRequest('Task status is required')
        
task_status_update_view = TaskStatusUpdateView.as_view()


# permission to check assigned_to and manager can only view this page
class TaskUpdatesView(LoginRequiredMixin, TemplateView):
    template_name = 'home/task_update.html'
    login_url = 'users:login'
    form_class = TaskUpdatesForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_id = self.kwargs['task_id']
        try:
            form = self.form_class
            task = Task.objects.get(id=task_id)
            updates = TaskUpdates.objects.filter(task__id=task_id)
            context['task'] = task
            context['updates'] = updates
            context['form'] = form
        except TaskUpdates.DoesNotExist:
            raise HttpResponseNotFound("No Task Updates Found")
        return context

    def post(self, request, *args, **kwargs):
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, id=task_id)
        user = request.user
        form = TaskUpdatesForm(request.POST)
        if form.is_valid():
            form.save(task, user)
            form = self.form_class()
            updates = TaskUpdates.objects.filter(task__id=task_id)
            return self.render_to_response({'form': form, 'updates': updates})
        else:
            return HttpResponseBadRequest('Message error')

task_updates_view = TaskUpdatesView.as_view()
