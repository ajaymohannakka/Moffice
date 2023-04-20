from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from .forms import UserProfileForm, AddRoleForm
from project_management.utils.permissions import HRLevelPermissionMixin
from project_management.teams.models import Role
from project_management.users.models import User


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home/index.html'
    login_url = 'users:login'

home_view = HomeView.as_view()


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'home/profile.html'
    login_url = 'users:login'
    form_class = UserProfileForm

    def get(self, request, *args, **kwargs):
        user = request.user
        form = self.form_class({'first_name': user.first_name, 'last_name': user.last_name, 'bio': user.bio})
        return self.render_to_response({'form': form})

    def post(self, request, *args, **kwargs):
        user=request.user
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save(user)
            data = {'success': True, 'message': 'Data saved successfully!'}
            return JsonResponse(data)
        return self.render_to_response({'form': form})

profile_view = ProfileView.as_view()


class RolesView(LoginRequiredMixin, HRLevelPermissionMixin, TemplateView):
    template_name = "home/roles_page.html"
    login_url = 'users:login'
    form_class = AddRoleForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            form = self.form_class
            company = self.request.user.company
            roles = Role.objects.filter(company=company)
            context['roles'] = roles
            context['form'] = form
        except Role.DoesNotExist:
            raise Http404("Roles does not exist")
        return context

    def post(self, request, *args, **kwargs):
        company = request.user.company
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save(company)
            data = {'success': True, 'message': 'Data saved successfully!'}
            return JsonResponse(data)
        return self.render_to_response({'form': form})

roles_view = RolesView.as_view()


class VerifyUserView(LoginRequiredMixin, HRLevelPermissionMixin, ListView):
    template_name = "home/verify_user_page.html"
    login_url = 'users:login'
    model = User
    context_object_name = 'users'

    def get_queryset(self):
        queryset = super().get_queryset()
        company = self.request.user.company
        return queryset.filter(company=company, is_active=False)
    
    def patch(self, request, *args, **kwargs):
        user_id = kwargs['user_id']
        user = get_object_or_404(User, id=user_id, is_active=False)
        user.is_active = True
        user.save()
        data = {'success': True, 'message': 'Data saved successfully!'}
        return JsonResponse(data)

    def delete(self, request, *args, **kwargs):
        user_id = kwargs['user_id']
        user = get_object_or_404(User, id=user_id, is_active=False)
        user.delete()
        data = {'success': True, 'message': 'Data saved successfully!'}
        return JsonResponse(data)


verify_user_view = VerifyUserView.as_view()


class VerifiedUserView(LoginRequiredMixin, HRLevelPermissionMixin, ListView):
    template_name = 'home/verified_user_page.html'
    login_url = 'users:login'
    model = User
    context_object_name = 'users'

    def get_queryset(self):
        queryset = super().get_queryset()
        company = self.request.user.company
        return queryset.filter(company=company, is_active=True)    

verified_user_view = VerifiedUserView.as_view()
