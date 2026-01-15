from django.core.exceptions import PermissionDenied

def solo_super_autorizados(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        # Lista de nombres de usuario con poder absoluto
        # Reemplaza con tus nombres de usuario reales
        autorizados = ['tu_usuario_programador', 'director_sociales']
        if request.user.is_authenticated and request.user.username in autorizados:
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied # Lanza un error 403 (Prohibido)
    return _wrapped_view_func