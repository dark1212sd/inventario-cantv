from django.db import models
from django.contrib.auth.models import User

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