from django.urls import path
from .views import *

app_name = 'tasks'

urlpatterns = [
    path('project/<int:project_id>/create-task/', create_task_view, name='create_task'),
    path('updates/<int:task_id>/', task_updates_view, name='task_updates'),
    path('update-status/<int:task_id>/', task_status_update_view, name='update_task')
]
