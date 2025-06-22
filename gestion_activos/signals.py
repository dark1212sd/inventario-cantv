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
    Crea un perfil para cada nuevo usuario y se asegura de que exista al guardar.
    """
    if created:
        Perfil.objects.create(user=instance)

    # Esta línea asegura que el perfil se guarde, pero puede fallar si no existe.
    # La envolvemos en un bloque try/except para robustez, aunque el paso 2 es la solución real.
    try:
        instance.perfil.save()
    except Perfil.DoesNotExist:
        # Si el perfil no existe por alguna razón (como en usuarios antiguos), lo creamos.
        Perfil.objects.create(user=instance)