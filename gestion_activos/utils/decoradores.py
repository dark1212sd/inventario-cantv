from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect


def grupo_requerido(nombre_grupo):
    def check(user):
        return user.is_authenticated and user.groups.filter(name=nombre_grupo).exists()

    return user_passes_test(check, login_url='sin_permisos')
