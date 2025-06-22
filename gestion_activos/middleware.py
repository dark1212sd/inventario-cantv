from django.shortcuts import redirect
from django.urls import reverse


class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # El middleware se ejecuta en cada petición

        # Nos aseguramos de que el usuario esté logueado y no sea un superusuario
        # para no bloquearnos a nosotros mismos del admin.
        if request.user.is_authenticated and not request.user.is_superuser:

            # Usamos la bandera que ya habíamos creado
            if not request.user.perfil.info_personal_confirmada:

                # Lista de URLs a las que SÍ permitimos acceso
                allowed_urls = [
                    reverse('ver_perfil'),
                    reverse('logout')
                ]

                # Si el usuario intenta ir a cualquier otra URL, lo redirigimos a su perfil
                if request.path not in allowed_urls:
                    return redirect('ver_perfil')

        response = self.get_response(request)
        return response