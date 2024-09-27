from django.contrib import admin

from server.alumnos.models import Alumno

# Register the model in the admin site

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    """
    Admin class for the Alumno model.
    """
    list_display = ("user_full_name", "legajo", "user_email", "user_dni")
    list_filter = ()
    search_fields = list_display
    ordering = ("user",)
    filter_horizontal = ()

    def user_email(self, obj):
        return obj.user.email

    def user_full_name(self, obj):
        return obj.user.full_name

    def user_dni(self, obj):
        return obj.user.dni

    def user_group(self, obj):
        return obj.user.groups.all()
