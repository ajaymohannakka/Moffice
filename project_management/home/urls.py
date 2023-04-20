from django.urls import path
from .views import home_view, profile_view, roles_view, verify_user_view, verified_user_view


app_name = 'home'

urlpatterns = [
    path('', home_view, name='index'),
    path('profile/', profile_view, name='profile'),
    path('roles/', roles_view, name='roles'),
    path('verify/', verify_user_view, name='verify'),
    path('verify/reject/<int:user_id>/', verify_user_view, name='reject_user'),
    path('verify/accept/<int:user_id>/', verify_user_view, name='accept_user'),
    path('verified-users/', verified_user_view, name='verified_user')
]
