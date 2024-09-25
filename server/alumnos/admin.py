from django.contrib import admin

from server.alumnos.models import Alumno


# Register the model in the admin site
@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    """
    Admin class for the Alumno model.
    """

    list_display = ("user", "user__dni", "user_id", "legajo")
    list_filter = ()
    search_fields = ("user__dni", "user__full_name", "legajo")
    ordering = ("user",)
    filter_horizontal = ()
