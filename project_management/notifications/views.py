from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from .utils import get_message_time
from .models import Notification


class UnseenNotificationListView(LoginRequiredMixin, View):
   
   def get(self, request, *args, **kwargs):
        user = self.request.user
        queryset = Notification.objects.filter(user=user, seen=False)
        unread_count = queryset.count()
        notifications = [
            {'message': n.message, 'sent_by': n.sent_by.get_full_name(), 'created': get_message_time(n.created_at)} 
            for n in queryset
            ]
        return JsonResponse({'unread_count': unread_count, 'notifications': notifications})

get_unseen_notification_list_view = UnseenNotificationListView.as_view()
