from django.shortcuts import render
from project_management.users.models import User


class NotEmployeePermissionMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.user_type == User.UserType.EMPLOYEE:
            return render(request, 'error/page-403.html')
        return super().dispatch(request, *args, **kwargs)


class HRLevelPermissionMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.user_type == User.UserType.EMPLOYEE or user.user_type == User.UserType.MANAGER:
            return render(request, 'error/page-403.html')
        return super().dispatch(request, *args, **kwargs)
