from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import Perfil


class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # El middleware se ejecuta en cada petición

        # Solo aplicamos la lógica para usuarios logueados
        if request.user.is_authenticated:

            try:
                perfil_confirmado = request.user.perfil.info_personal_confirmada
            except Perfil.DoesNotExist:
                # Si el perfil no existe, lo creamos y lo marcamos como no confirmado
                Perfil.objects.create(user=request.user)
                perfil_confirmado = False

            # Si la información no ha sido confirmada, forzamos la redirección
            if not perfil_confirmado:

                # Definimos a dónde debe ir cada tipo de usuario
                if request.user.is_staff:
                    # El personal administrativo va a su propia página de perfil
                    redirect_url = reverse('editar_perfil_staff')
                    allowed_urls = [redirect_url, reverse('logout')]
                else:
                    # Los usuarios finales van a la suya
                    redirect_url = reverse('completar_perfil')
                    allowed_urls = [redirect_url, reverse('logout')]

                # Si el usuario no está ya en una de las páginas permitidas, lo redirigimos
                if request.path not in allowed_urls:
                    messages.warning(request, 'Para continuar, por favor completa tu información personal.')
                    return redirect(redirect_url)

        response = self.get_response(request)
        return response