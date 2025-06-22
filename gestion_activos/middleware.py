from django.shortcuts import redirect
from django.urls import reverse

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            if not request.user.perfil.info_personal_confirmada:
                # Permitimos acceso a la nueva página de completar perfil y al logout
                allowed_urls = [reverse('completar_perfil'), reverse('logout')]
                if request.path not in allowed_urls:
                    # Redirigimos a la nueva vista
                    return redirect('completar_perfil')
        return self.get_response(request)