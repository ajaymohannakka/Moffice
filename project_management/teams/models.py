from django.db import models

from project_management.users.models import User, Company


class Role(models.Model):
    role = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.role
    

class Team(models.Model):
    team_name = models.CharField(max_length=50)
    team_description = models.CharField(max_length=1000)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    manager = models.ForeignKey(User, null=True, blank=False, on_delete=models.SET_NULL)

    def __str__(self):
        return self.team_name

    class Meta:
        unique_together = ('team_name', 'company')
    

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='teammember')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, default=None, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}({self.user.email})"

    class Meta:
        unique_together = ('team', 'user')
