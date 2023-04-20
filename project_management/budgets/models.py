from django.db import models
from django.utils.translation import gettext_lazy as _

from project_management.users.models import User
from project_management.projects.models import Project


class UserRate(models.Model):
    user_rate_per_hour = models.BigIntegerField(default=0)
    project = models.ForeignKey(Project, verbose_name=_("project"), on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE)

    def __str__(self):
        return f"""{self.user.first_name} {self.user.last_name} ({self.user.email}) 
                    per hour rate is {self.user_rate_per_hour}"""
