from django.contrib import admin

from server.alumnos.models import Alumno


# Register the model in the admin site
@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    """
    Admin class for the Alumno model.
    """

    list_display = ("user__full_name", "user__dni", "legajo")
    list_filter = ()
    search_fields = ("legajo", "user__dni")
    ordering = ("user",)
    filter_horizontal = ("groups", "user_permissions")
