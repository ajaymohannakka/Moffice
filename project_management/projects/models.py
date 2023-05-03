from django.db import models
from django.utils.translation import gettext_lazy as _

from project_management.teams.models import Team
from project_management.users.models import User


class Project(models.Model):
    project_name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    start_date_time = models.DateTimeField(_("start date"), auto_now=False, auto_now_add=False)
    end_date_time = models.DateTimeField(_("end date"), auto_now=False, auto_now_add=False)
    assigned_to = models.ForeignKey(Team, on_delete=models.CASCADE)
    
    class ProjectStatus(models.TextChoices):
        COMPLETED = 'CMP', _('Completed')
        PENDING = 'PEN', _('Pending')
    
    project_status = models.CharField(
        max_length=3,
        choices=ProjectStatus.choices,
        default=ProjectStatus.PENDING,
    )

    def get_project_completion_details(self):
        from project_management.tasks.models import Task
        total_tasks = self.task_set.count()
        completed_tasks = self.task_set.filter(task_status=Task.TaskStatus.COMPLETED).count()
        pending_tasks = total_tasks - completed_tasks

        completed_percent = round((completed_tasks / total_tasks) * 100) if total_tasks != 0 else 0
        pending_percent = round((pending_tasks / total_tasks) * 100) if total_tasks != 0 else 0

        return {'completed_percent': completed_percent, 'pending_percent': pending_percent}


class ProjectUpdates(models.Model):
    project = models.ForeignKey(Project, verbose_name=_("task"), on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE)
    created = models.DateTimeField(_("start date"), auto_now_add=True)
    message = models.TextField(_("update description"))
