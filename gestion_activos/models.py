from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings



class Categoria(models.Model):
    nombre      = models.CharField("Categoría", max_length=100, unique=True)
    descripcion = models.TextField("Descripción", blank=True)

    def __str__(self):
        return self.nombre

class Ubicacion(models.Model):
    nombre      = models.CharField("Ubicación", max_length=100, unique=True)
    descripcion = models.TextField("Descripción", blank=True)

    def __str__(self):
        return self.nombre

class Activo(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=[
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('en_mantenimiento', 'En mantenimiento')
    ])
    fecha_registro = models.DateTimeField(auto_now_add=True)

    # Nuevo campo
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='activos_responsables')

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'

class LogAccion(models.Model):
    ACCION_CREACION = 'CREACIÓN'
    ACCION_ACTUALIZACION = 'ACTUALIZACIÓN'
    ACCION_ELIMINACION = 'ELIMINACIÓN'

    ACCION_CHOICES = [
        (ACCION_CREACION, 'Creación'),
        (ACCION_ACTUALIZACION, 'Actualización'),
        (ACCION_ELIMINACION, 'Eliminación'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Usuario"
    )
    accion = models.CharField(
        max_length=20,
        choices=ACCION_CHOICES,
        verbose_name="Acción"
    )
    # Usamos ContentType para hacer una referencia genérica a cualquier modelo (Activo, Categoria, etc.)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="Tipo de Objeto"
    )
    object_id = models.PositiveIntegerField(verbose_name="ID del Objeto")
    content_object = GenericForeignKey('content_type', 'object_id')

    detalles = models.TextField(
        blank=True,
        null=True,
        verbose_name="Detalles"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y Hora"
    )

    def __str__(self):
        return f'{self.timestamp.strftime("%Y-%m-%d %H:%M")} - {self.usuario.username} - {self.get_accion_display()} en {self.content_type.model}'

    class Meta:
        verbose_name = 'Registro de Acción'
        verbose_name_plural = 'Registros de Acciones'
        ordering = ['-timestamp']