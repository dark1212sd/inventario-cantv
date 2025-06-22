# utils/signals.py o gestion_activos/signals.py
from django.db.models.signals import post_migrate, post_save
from django.contrib.auth.models import Group, Permission, User
from django.dispatch import receiver
from .models import Perfil

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

@receiver(post_save, sender=User)
def crear_o_actualizar_perfil_usuario(sender, instance, created, **kwargs):
    """
    Crea un perfil para cada nuevo usuario o guarda el perfil existente.
    """
    if created:
        Perfil.objects.create(user=instance)
    instance.perfil.save()