from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from server.alumnos.models import Alumno

def setup_groups_and_permissions(sender, **kwargs):
    #cear o obtener el grupo de Alumnos
    alumno_group, _ = Group.objects.get_or_create(name='Alumnos')

    # def permisos para el grupo de Alumnos
    alumno_content_type = ContentType.objects.get_for_model(Alumno)
    view_alumno_permission, _ = Permission.objects.get_or_create(
        codename='view_alumno',
        name='Can view alumno',
        content_type=alumno_content_type,
    )

    #se signa permisos al grupo de Alumnos
    alumno_group.permissions.add(view_alumno_permission)

    #crear o obtener el grupo de Staff
    staff_group, _ = Group.objects.get_or_create(name='Staff')

    #definir permisos para el grupo de Staff
    staff_permissions = [
        'add_alumno',
        'change_alumno',
        'delete_alumno',
        'view_alumno',
    ]

    #se asignan permisos al grupo de Staff
    for perm in staff_permissions:
        permission = Permission.objects.get(
            codename=perm,
            content_type=alumno_content_type
        )
        staff_group.permissions.add(permission)

    # print("Grupos y permisos configurados correctamente.")
