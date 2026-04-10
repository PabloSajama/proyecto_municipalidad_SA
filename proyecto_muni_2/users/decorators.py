from django.core.exceptions import PermissionDenied
from functools import wraps
from django.shortcuts import redirect
from .models import OperadorMunicipal, RolMunicipal

def solo_super_autorizados(view_func):
    """Solo permite el acceso si el usuario es SUPER."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Verificamos si tiene perfil de operador y si su rol es SUPER
        if hasattr(request.user, 'operador') and request.user.operador.rol == RolMunicipal.SUPER_USUARIO:
            return view_func(request, *args, **kwargs)
            
        raise PermissionDenied
    return _wrapped_view

def tiene_permiso(nombre_area_objetivo, requiere_admin=False):
    """
    Controla acceso por Área y Nivel de Rol.
    nombre_area_objetivo: El nombre del área (ej: 'SOCIALES')
    requiere_admin: Si es True, solo ADMIN o SUPER pueden entrar.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # 1. El Súper Usuario (Django Superuser) siempre pasa
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # 2. Obtenemos el perfil laboral
            operador = getattr(request.user, 'operador', None)
            
            if not operador or not operador.activo:
                raise PermissionDenied

            # 3. Verificamos Área (Ignoramos mayúsculas/minúsculas)
            area_correcta = operador.area.nombre.upper() == nombre_area_objetivo.upper()
            
            # 4. Verificamos Jerarquía de Rol
            if area_correcta:
                # Si se requiere ser admin, revisamos si es ADMIN o SUPER
                if requiere_admin:
                    if operador.rol in [RolMunicipal.ADMINISTRADOR, RolMunicipal.SUPER_USUARIO]:
                        return view_func(request, *args, **kwargs)
                else:
                    # Si no requiere ser admin, cualquier rol municipal del área pasa
                    return view_func(request, *args, **kwargs)

            raise PermissionDenied
        return _wrapped_view
    return decorator