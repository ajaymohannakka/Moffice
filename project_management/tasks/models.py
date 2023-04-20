from django.db import models
from django.utils.translation import gettext_lazy as _

from project_management.projects.models import Project
from project_management.users.models import User


class Task(models.Model):
    # belog to which project
    belong_to = models.ForeignKey(Project, on_delete=models.CASCADE)
    # assigned to which user
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date_time = models.DateTimeField(_("start date"), auto_now=False, blank=True, null=True, auto_now_add=False)
    end_date_time = models.DateTimeField(_("end date"), blank=True, null=True, auto_now=False, auto_now_add=False)
    task_name = models.CharField(max_length=50)
    description = models.TextField()

    class TaskStatus(models.TextChoices):
        COMPLETED = 'CMP', _('Completed')
        ONGOING = 'INP', _('In Progress')
        REVIEW = 'REV', _('In Review')
        TODO = 'TOD', _('TODO')

    task_status = models.CharField(
        max_length=3,
        choices=TaskStatus.choices,
        default=TaskStatus.TODO,
    )

    def __str__(self):
        return self.task_name

    # get_hours_worked on a task
    # get cost of a task
    

class TaskUpdates(models.Model):
    task = models.ForeignKey(Task, verbose_name=_("task"), on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE)
    created = models.DateTimeField(_("start date"), auto_now_add=True)
    update_description = models.TextField(_("update description"))
