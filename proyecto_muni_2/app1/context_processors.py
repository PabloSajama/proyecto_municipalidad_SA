# app1/context_processors.py

def permisos_roles(request):
    if not request.user.is_authenticated:
        return {}
    
    user = request.user
    perfil = getattr(user, 'perfil', None)
    area = perfil.area if perfil else None
    
    # Verificamos grupos
    es_admin = user.groups.filter(name='Administrador').exists() or user.is_superuser
    es_operador = user.groups.filter(name='Operador').exists()
    
    # Es empleado si tiene alguno de los dos roles
    es_empleado = es_admin or es_operador

    return {
        'es_admin_catastro': area == 'CATASTRO' and es_admin,
        'es_personal_catastro': area == 'CATASTRO' and es_empleado,
        'es_admin_comercio': area == 'COMERCIO' and es_admin,
        'es_personal_comercio': area == 'COMERCIO' and es_empleado,
        'es_admin_gral': area == 'ADMIN_GRAL' or user.is_superuser,
        'es_empleado': es_empleado, # <--- Nueva variable útil
    }