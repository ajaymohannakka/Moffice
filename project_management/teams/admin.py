from django.contrib import admin

from .models import Team, TeamMember, Role
# Register your models here.

admin.site.register(Team)
admin.site.register(TeamMember)
admin.site.register(Role)
