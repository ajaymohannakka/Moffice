from django.urls import path

from .views import *

app_name = 'budgets'

urlpatterns = [
    path('list/', manage_budget_list_view, name='budget_list'),
    path('list-users/', user_list_view, name='list_users'),
    path('user-budget/<int:user_id>/', user_budget_view, name='user_budget')
]
