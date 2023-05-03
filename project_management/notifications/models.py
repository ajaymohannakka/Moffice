from django.db import models
from django.utils.translation import gettext_lazy as _

from project_management.users.models import User


class Notification(models.Model):
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE)
    message = models.CharField(_("message"), max_length=50)
    seen = models.BooleanField(_("seen notification"), default=False)
    sent_by = models.ForeignKey(
        User, 
        related_name='sent_by_user', 
        verbose_name=_("notification sent by"), 
        default=None, 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE
        )
    created_at = models.DateTimeField(_("notification time"), auto_now=False, auto_now_add=False)
