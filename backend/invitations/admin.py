from django.contrib import admin

from .models import Invitation


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("code", "first_name", "last_name", "event_type", "event_at", "views", "created_at")
    search_fields = ("code", "first_name", "last_name")
    readonly_fields = ("code", "views", "created_at")
    list_filter = ("event_type", "theme")
