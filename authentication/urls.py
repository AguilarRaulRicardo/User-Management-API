from django.urls import re_path
from .views import register, login, log

urlpatterns= [
    re_path('register', register),
    re_path('login', login),
    re_path('log', log),
]