from django.urls import path

from .views import get_unseen_notification_list_view

app_name = 'notifications'

urlpatterns = [
    path('list-unseen/', get_unseen_notification_list_view, name='list_unseen')
]
