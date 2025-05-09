from django.db import models

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
    codigo = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)
    ubicacion = models.ForeignKey('Ubicacion', on_delete=models.CASCADE)
    ESTADOS = [
        ('activo', 'Activo'),
        ('mant', 'En mantenimiento'),
        ('baja', 'Dado de baja'),
    ]

    estado = models.CharField(max_length=10, choices=ESTADOS, default='activo')
    fecha_registro = models.DateField(auto_now_add=True)  # <- esto hace que se genere automáticamente

    def __str__(self):
        return self.nombre
