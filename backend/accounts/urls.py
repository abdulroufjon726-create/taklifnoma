from django.urls import path

from . import views

urlpatterns = [
    path("auth/google/start/", views.google_start, name="google-start"),
    path("auth/google/callback/", views.google_callback, name="google-callback"),
    path("auth/register/", views.register, name="auth-register"),
    path("auth/login/", views.password_login, name="auth-login"),
    path("auth/me/", views.me, name="auth-me"),
    path("auth/logout/", views.logout, name="auth-logout"),
    path("auth/password/", views.set_password, name="auth-password"),
    path("auth/config/", views.auth_config, name="auth-config"),
]
