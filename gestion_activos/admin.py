from django.contrib import admin
from .models import Categoria, Ubicacion, Activo
from django.contrib.auth.decorators import user_passes_test

@admin.register(Activo)
class ActivoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'categoria', 'ubicacion', 'fecha_registro', 'estado')
    search_fields = ('nombre', 'codigo')
    list_filter = ('categoria', 'estado', 'ubicacion')

# Registros simples para los otros modelos
admin.site.register(Categoria)
admin.site.register(Ubicacion)
# Register your models here.


def grupo_requerido(nombre_grupo):
    def check(user):
        return user.is_authenticated and user.groups.filter(name=nombre_grupo).exists()
    return user_passes_test(check)
