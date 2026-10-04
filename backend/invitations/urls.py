from django.urls import path

from . import views

urlpatterns = [
    path("invitations/", views.invitation_create, name="invitation-create"),
    path("invitations/<str:code>/", views.invitation_detail, name="invitation-detail"),
]
