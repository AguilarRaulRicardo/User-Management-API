from django.urls import re_path
from .views import register, login, log, update, delete

urlpatterns= [
    re_path('register', register),
    re_path('login', login),
    re_path('log', log),
    re_path('update', update),
    re_path('delete', delete),
]