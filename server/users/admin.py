from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Admin class for the User model.
    """

    list_display = ("dni", "full_name", "email")
    list_filter = ("groups",)
    search_fields = list_display
    ordering = ("full_name",)
    filter_horizontal = ("groups", "user_permissions")
