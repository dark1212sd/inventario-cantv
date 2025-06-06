# gestion_activos/utils/decoradores.py

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def grupo_requerido(nombre_grupo):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.groups.filter(name=nombre_grupo).exists():
                return view_func(request, *args, **kwargs)
            return redirect('sin_permisos')
        return _wrapped_view
    return decorator

# Decoradores específicos
auditor_required = grupo_requerido('Auditor')
tecnico_required = grupo_requerido('Técnico')
administrador_required = grupo_requerido('Administrador')