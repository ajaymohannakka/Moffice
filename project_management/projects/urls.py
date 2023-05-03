from django.urls import path
from .views import *

app_name = 'projects'

urlpatterns = [
    path('list/', projects_view, name='project_list'),
    path('create/', create_project_view, name='create_project'),
    path('details/<int:project_id>/', project_details_view, name='project_details'),
    path('<int:project_id>/discuss/', project_discuss_view, name='discuss_project'),
    path('details/<int:project_id>/completion-data/', project_completion_graph_data, name='completion_data'),
    path('details/<int:project_id>/line-data/', project_progress_graph_data, name='line_data'),
    path('<int:project_id>/update-status/', project_status_update_view, name='Project_completed')
]
