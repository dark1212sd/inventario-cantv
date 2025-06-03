# utils/signals.py o gestion_activos/signals.py
from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.dispatch import receiver

@receiver(post_migrate)
def crear_roles(sender, **kwargs):
    roles = {
        'Administrador': Permission.objects.all(),
        'Supervisor': Permission.objects.filter(codename__in=[
            'view_activo', 'change_activo'
        ]),
        'Usuario': Permission.objects.filter(codename__in=[
            'view_activo'
        ]),
    }

    for nombre_rol, permisos in roles.items():
        grupo, creado = Group.objects.get_or_create(name=nombre_rol)
        grupo.permissions.set(permisos)
        grupo.save()