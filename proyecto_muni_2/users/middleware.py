from django.shortcuts import redirect
from django.urls import reverse

class PasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Verificamos si es operador y si tiene el cambio pendiente
            operador = getattr(request.user, 'operador', None)
            if operador and operador.requiere_cambio_password:
                # Si intenta ir a cualquier lado que no sea cambiar-clave o logout, lo regresamos
                ruta_permitida = [
                    reverse('cambiar_password_operador'),
                    reverse('logout'),
                ]
                if request.path not in ruta_permitida and not request.path.startswith('/static/'):
                    return redirect('cambiar_password_operador')

        return self.get_response(request)