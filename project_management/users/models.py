from datetime import timedelta

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.db import models

from .managers import CustomUserManager


class Company(models.Model):
    company_name = models.CharField(max_length=500, unique=True)
    
    def __str__(self):
        return self.company_name


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    bio = models.TextField(_("user bio"), null=True, blank=True, default="")
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class UserType(models.TextChoices):
        COMPANY_OWNER = 'CO', _('Company Owner')
        MANAGER = 'MA', _('Manager')
        EMPLOYEE = 'EM', _('Employee')
        HR = 'HR', _('HR')

    user_type = models.CharField(
        max_length=2,
        choices=UserType.choices,
        default=UserType.EMPLOYEE,
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def get_task_stats(self, project):
        from project_management.tasks.models import Task
        total_tasks = Task.objects.filter(belong_to=project, assigned_to=self).count()
        tasks_completed = Task.objects.filter(belong_to=project, assigned_to=self, task_status=Task.TaskStatus.COMPLETED).count()
        return int((tasks_completed/total_tasks)*100) if total_tasks != 0 else 0

    def get_total_working_hours(self, project):
        from project_management.tasks.models import Task
        completed_tasks = Task.objects.filter(belong_to=project, assigned_to=self, task_status=Task.TaskStatus.COMPLETED)
        total_time = timedelta()
        for task in completed_tasks:
            if task.start_date_time and task.end_date_time:
                time_spent = task.end_date_time - task.start_date_time
                total_time += time_spent
        working_hours = (total_time.days * 8.) + (total_time.seconds / 3600.0)
        return working_hours

    def get_full_name(self):
        if self.first_name and self.last_name:
            return self.first_name+ ' ' + self.last_name
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return ''

    objects = CustomUserManager()
