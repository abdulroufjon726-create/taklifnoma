from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health, name="health"),
    path("invitations/", views.invitation_create, name="invitation-create"),
    path("invitations/mine/", views.invitation_mine, name="invitation-mine"),
    path("invitations/<str:code>/", views.invitation_detail, name="invitation-detail"),
    path("invitations/<str:code>/claim/", views.invitation_claim, name="invitation-claim"),
]
