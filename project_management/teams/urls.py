from django.urls import path
from .views import *

app_name = 'teams'

urlpatterns = [
    path('list/', teams_view, name='team_list'),
    path('create/', create_team_view, name='create_team'),
    path('details/<int:team_id>/', details_team_view, name='team_details')
]
