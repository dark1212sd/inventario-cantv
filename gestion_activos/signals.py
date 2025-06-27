from django.db.models.signals import post_migrate, post_save
from django.contrib.auth.models import Group, Permission, User
from django.dispatch import receiver
from .models import Perfil


@receiver(post_migrate)
def crear_roles_y_permisos(sender, **kwargs):
    """
    Crea o actualiza los roles (Grupos) del sistema y les asigna
    un conjunto de permisos predefinido.
    """
    # Definimos los conjuntos de permisos para cada rol
    permisos_tecnico = Permission.objects.filter(codename__in=[
        'view_activo',
        'add_activo',
        'change_activo',
        'view_categoria',
        'view_ubicacion',
    ])

    permisos_auditor = Permission.objects.filter(codename__in=[
        'view_activo',
        'view_categoria',
        'view_ubicacion',
        'view_user',
        'view_perfil',
        'view_logaccion',
    ])

    permisos_supervisor = Permission.objects.filter(codename__in=[
        'view_activo', 'add_activo', 'change_activo'
    ])

    # Diccionario central de roles y sus permisos
    roles = {
        'Administrador': Permission.objects.all(),
        'Supervisor': permisos_supervisor,
        'Técnico': permisos_tecnico,  # <-- NUEVO ROL AÑADIDO
        'Auditor': permisos_auditor,  # <-- NUEVO ROL AÑADIDO
        'Usuario': Permission.objects.filter(codename__in=['view_activo']),
    }

    print("Creando y/o actualizando roles del sistema...")
    for nombre_rol, permisos_rol in roles.items():
        grupo, creado = Group.objects.get_or_create(name=nombre_rol)
        grupo.permissions.set(permisos_rol)
        if creado:
            print(f"-> Grupo '{nombre_rol}' creado exitosamente.")
        else:
            print(f"-> Permisos del grupo '{nombre_rol}' actualizados.")


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Crea un perfil automáticamente para cada nuevo usuario.
    """
    if created:
        Perfil.objects.get_or_create(user=instance)
