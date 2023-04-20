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

    def get_full_name(self):
        return self.first_name+ ' ' + self.last_name

    objects = CustomUserManager()
