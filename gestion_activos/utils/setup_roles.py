# utils/setup_roles.py
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from gestion_activos.models import Activo  # Asegúrate que este modelo existe

def crear_roles():
    # Administrador del Sistema
    admin_group, _ = Group.objects.get_or_create(name='Administrador del Sistema')
    admin_permissions = Permission.objects.all()
    admin_group.permissions.set(admin_permissions)

    # Técnico de Soporte TI
    soporte_group, _ = Group.objects.get_or_create(name='Técnico de Soporte TI')
    soporte_permissions = Permission.objects.filter(codename__in=[
        'add_activo', 'change_activo', 'delete_activo', 'view_activo',
    ])
    soporte_group.permissions.set(soporte_permissions)

    # Coordinador de Inventario
    coord_group, _ = Group.objects.get_or_create(name='Coordinador de Inventario')
    coord_permissions = Permission.objects.filter(codename__in=[
        'view_activo', 'change_activo',
    ])
    coord_group.permissions.set(coord_permissions)

    print("Roles y permisos asignados correctamente.")