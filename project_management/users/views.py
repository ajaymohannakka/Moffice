from django.shortcuts import render, redirect
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import View
from django.contrib.auth import authenticate, login

from .forms import LoginForm, SignUpForm, CreateCompanyForm
from .models import User


class IsUserAuthenticatedMixin:
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:index')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})


class UserLoginView(IsUserAuthenticatedMixin, View):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            status = User.objects.filter(email=email)
            if user is not None:
                login(request, user)
                return redirect('home:index')
            elif status.values() and not status.values()[0]['is_active']:
                form.add_error(None, 'Your account is not been verified')
            else:
                form.add_error(None, 'Invalid login credentials')
        return render(request, self.template_name, {'form': form})

get_login = UserLoginView.as_view()


class UserRegisterView(IsUserAuthenticatedMixin, CreateView):
    template_name = 'accounts/register.html'
    form_class = SignUpForm
    success_url = reverse_lazy('users:login')

get_register = UserRegisterView.as_view()


class CreateCompanyView(IsUserAuthenticatedMixin, CreateView):
    template_name = 'accounts/create.html'
    form_class = CreateCompanyForm
    success_url = reverse_lazy('users:register')

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:register')
        return render(request, self.template_name, {'form': form})

create_company = CreateCompanyView.as_view()


class UserLogoutView(LogoutView):
    next_page = 'users:login'

get_logout = UserLogoutView.as_view()
