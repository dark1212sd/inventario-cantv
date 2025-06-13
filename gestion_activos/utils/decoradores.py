from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.shortcuts import redirect

def grupo_requerido(*nombres_grupos):
    """
    Verifica si el usuario pertenece a al menos uno de los grupos especificados.
    Redirige a la vista 'sin_permisos' si no pertenece.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.groups.filter(name__in=nombres_grupos).exists():
                return view_func(request, *args, **kwargs)
            return redirect('sin_permisos')
        return _wrapped_view
    return decorator