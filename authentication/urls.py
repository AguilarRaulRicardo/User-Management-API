from django.urls import re_path, path
from .views import (
    register,
    login,
    log,
    update,
    delete,
    validate_user,
    validate_staff,
    make_staff,
    change_password,
)

urlpatterns = [
    re_path("register", register),
    re_path("login", login),
    re_path("log", log),
    re_path("update", update),
    re_path("delete", delete),
    re_path("validate_user", validate_user),
    re_path("validate_staff", validate_staff),
    re_path("make_staff", make_staff),
    re_path("change_password", change_password),
]

