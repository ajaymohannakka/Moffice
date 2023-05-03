from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from project_management.projects.models import ProjectUpdates
from project_management.users.models import User
from project_management.notifications.models import Notification 


@receiver(post_save, sender=ProjectUpdates)
def create_project_updates_notification(sender, instance, created, **kwargs):
    """
    Creates a notification for all users belonging to the project whenever a new message is added to ProjectUpdates.
    """
    if created:
        project = instance.project
        sent_by = instance.user
        users = project.assigned_to.teammember.exclude(user=instance.user).distinct().values_list('user', flat=True)
        users = list(users)
        team_manager = project.assigned_to.manager
        if team_manager != instance.user and team_manager not in users:
            users.append(team_manager.id)
        message = instance.message

        # Create notification for each user
        for user_id in users:
            user = User.objects.get(id=user_id)
            notification = Notification.objects.create(
                user=user,
                message=message,
                sent_by=sent_by,
                created_at=timezone.now()
            )
