from django.urls import path, include
from .views import *

app_name = "users"

urlpatterns = [
    path('login/', get_login, name='login'),
    path('register/', get_register, name='register'),
    path('logout/', get_logout, name='logout'),
    path('create-company/', create_company, name='create_company')
]
