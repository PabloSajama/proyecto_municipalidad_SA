from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
# Modelos y Forms
from django.utils import timezone
from .models import EventosSociales, ConsultasSociales, Reclamo
from .forms import EventoSocialForm, ConsultaSocialForm, RespuestaConsultaForm, RespuestaReclamoForm, ReclamoForm
from portal.utils import registrar_historial
from users.models import RolMunicipal, OperadorMunicipal
from portal.models import Contacto, ConfiguracionSector, AccesoDirecto, ComponenteSector
from users.utils import get_pantalla_data

# ==========================================================
# 1. HELPER DE SEGURIDAD (SOLO ROL)
# ==========================================================

def _tiene_rol_social(user):
    """Verifica únicamente si el usuario tiene el rango jerárquico."""
    if user.is_superuser:
        return True
    op = getattr(user, 'operador', None)
    return op and op.rol in [RolMunicipal.SUPER_USUARIO, RolMunicipal.ADMINISTRADOR]


# ==========================================================
# 2. VISTAS
# ==========================================================

def inicio_social(request):
    context = get_pantalla_data(area_name="SOCIAL", slug="inicio_social")
    if not context:
        raise Http404("La configuración para esta pantalla no existe.")
    return render(request, "social/inicio_social.html", context)


def lista_eventos_sociales(request):
    eventos = EventosSociales.objects.filter(activo=True)
    return render(request, 'eventos_sociales/lista_eventos.html', {'eventos': eventos})


@login_required
def crear_evento_social(request):
    # SEGURIDAD DE OPERADOR ACTIVO
    op = getattr(request.user, 'operador', None)
    if op and not op.operador_activo:
        logout(request)
        messages.error(request, "Su cuenta de operador ha sido desactivada.")
        return redirect('login')

    # SEGURIDAD DE ROL
    if not _tiene_rol_social(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        form = EventoSocialForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.activo = True 
            if op:
                evento.area = op.area 
            evento.save()
            
            registrar_historial(request.user, "CREAR", "EVENTOS_SOCIALES", f"Social: {evento.titulo}", evento.id_social)
            messages.success(request, f"Evento '{evento.titulo}' creado.")
            return redirect('social:lista_eventos')
    else:
        form = EventoSocialForm(initial={'activo': True})
    
    return render(request, 'eventos_sociales/crear_evento_social.html', {'form': form})


@login_required
def editar_evento_social(request, id_social):
    # SEGURIDAD DE OPERADOR ACTIVO
    op = getattr(request.user, 'operador', None)
    if op and not op.operador_activo:
        logout(request)
        messages.error(request, "Su cuenta de operador ha sido desactivada.")
        return redirect('login')

    evento = get_object_or_404(EventosSociales, id_social=id_social)
    
    # SEGURIDAD DE ROL
    if not _tiene_rol_social(request.user):
        messages.error(request, "No tienes permisos para editar eventos.")
        return redirect('social:lista_eventos')

    if request.method == 'POST':
        form = EventoSocialForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            form.save()
            registrar_historial(request.user, "EDITAR", "EVENTOS_SOCIALES", f"Editó: {evento.titulo}", id_social)
            messages.success(request, "Los cambios han sido guardados.")
            return redirect('social:lista_eventos')
    else:
        form = EventoSocialForm(instance=evento)
    
    return render(request, 'eventos_sociales/editar_evento_social.html', {'form': form, 'evento': evento})


@login_required
def eliminar_evento_social(request, id_social):
    # SEGURIDAD DE OPERADOR ACTIVO
    op = getattr(request.user, 'operador', None)
    if op and not op.operador_activo:
        logout(request)
        messages.error(request, "Su cuenta de operador ha sido desactivada.")
        return redirect('login')

    # SEGURIDAD DE ROL
    if not _tiene_rol_social(request.user):
        raise PermissionDenied
        
    evento = get_object_or_404(EventosSociales, id_social=id_social)
    
    if request.method == 'POST':
        evento.activo = False
        evento.save()
        registrar_historial(request.user, "ELIMINAR", "EVENTOS_SOCIALES", f"Baja: {evento.titulo}", id_social)
        messages.warning(request, "El evento ha sido retirado.")
    
    return redirect('social:lista_eventos')



## ==========================================================
## Consultas Sociales
## ==========================================================

# ==========================================================
# 3. VISTAS DE CONSULTAS SOCIALES
# ==========================================================

@login_required
def crear_consulta(request):
    """
    Accesible para TODO usuario autenticado en el sistema.
    """
    # Si el usuario es un operador pero está desactivado, lo sacamos
    op = getattr(request.user, 'operador', None)
    if op and not op.operador_activo:
        logout(request)
        messages.error(request, "Cuenta desactivada.")
        return redirect('login')

    if request.method == 'POST':
        form = ConsultaSocialForm(request.POST)
        if form.is_valid():
            consulta = form.save(commit=False)
            consulta.usuario = request.user  # Asignamos al ciudadano logueado
            consulta.save()
            
            # Historial con el nombre del área de destino
            registrar_historial(
                request.user, 
                "CREAR", 
                "CONSULTAS_SOCIALES", 
                f"Consulta enviada a {consulta.area_destino.nombre}: {consulta.asunto}", 
                consulta.id_consulta
            )
            
            messages.success(request, "Consulta enviada correctamente. El área correspondiente le responderá pronto.")
            return redirect('social:inicio-social')
    else:
        form = ConsultaSocialForm()
    
    return render(request, 'consultas_sociales/crear_consulta.html', {'form': form})

@login_required
def lista_consultas(request):
    """
    SOLO OPERADORES: Ven consultas dirigidas a SU área.
    """
    op = getattr(request.user, 'operador', None)
    
    # Verificación de seguridad: debe ser operador y tener un área asignada
    if not op or not op.operador_activo or not op.area:
        raise PermissionDenied

    # Filtro estricto: Solo mi área y no respondidas
    queryset = ConsultasSociales.objects.filter(
        area_destino=op.area, 
        respondida=False
    ).order_by('-fecha_envio')

    # ... (Mantenemos tu lógica de buscador Q y paginación igual) ...
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(Q(asunto__icontains=query) | Q(usuario__username__icontains=query))
    
    fecha_filtro = request.GET.get('fecha_filtro')
    if fecha_filtro:
        queryset = queryset.filter(fecha_envio__date=fecha_filtro)

    paginator = Paginator(queryset, 10)
    consultas = paginator.get_page(request.GET.get('page'))

    return render(request, 'consultas_sociales/lista_consultas.html', {
        'consultas': consultas, 
        'query': query,
        'fecha_filtro': fecha_filtro
    })

@login_required
def ver_consulta(request, id_consulta):
    """
    Ver detalle y RESPONDER la consulta.
    """
    op = getattr(request.user, 'operador', None)
    if op and not op.operador_activo:
        logout(request)
        return redirect('login')

    if not _tiene_rol_social(request.user):
        raise PermissionDenied

    # Solo puede verla si es de su área
    consulta = get_object_or_404(ConsultasSociales, id_consulta=id_consulta, area_destino=op.area)

    if request.method == 'POST':
        form = RespuestaConsultaForm(request.POST, instance=consulta)
        if form.is_valid():
            consulta_resp = form.save(commit=False)
            consulta_resp.respondida = True
            consulta_resp.fecha_respuesta = timezone.now()
            consulta_resp.save()
            
            registrar_historial(request.user, "EDITAR", "CONSULTAS_SOCIALES", 
                              f"Respondió consulta: {consulta.asunto}", id_consulta)
            
            messages.success(request, "La respuesta ha sido enviada al ciudadano.")
            return redirect('social:lista_consultas')
    else:
        form = RespuestaConsultaForm(instance=consulta)

    return render(request, 'consultas_sociales/ver_consulta.html', {
        'consulta': consulta,
        'form': form
    })

@login_required
def borrar_logico_consulta(request, id_consulta):
    """
    Archiva la consulta sin enviar respuesta necesariamente.
    """
    op = getattr(request.user, 'operador', None)
    if op and not op.operador_activo:
        logout(request)
        return redirect('login')

    if not _tiene_rol_social(request.user):
        raise PermissionDenied

    consulta = get_object_or_404(ConsultasSociales, id_consulta=id_consulta, area_destino=op.area)
    
    if request.method == 'POST':
        consulta.respondida = True
        # Si se archiva sin respuesta, podemos dejar una nota interna o simplemente marcar como respondida
        consulta.save()
        registrar_historial(request.user, "ELIMINAR", "CONSULTAS_SOCIALES", f"Archivó consulta: {consulta.asunto}", id_consulta)
        messages.warning(request, "La consulta ha sido archivada.")
    
    return redirect('social:lista_consultas')

@login_required
def mis_consultas(request):
    # Filtramos SOLO las consultas donde el 'usuario' es el que hace la petición
    consultas = ConsultasSociales.objects.filter(usuario=request.user).order_by('-fecha_envio')
    
    return render(request, 'consultas_sociales/mis_consultas.html', {
        'consultas': consultas,
    })

@login_required
def ver_consulta_personal(request, id_consulta):
    # Filtramos por ID y por el usuario actual por seguridad
    consulta = get_object_or_404(ConsultasSociales, id_consulta=id_consulta, usuario=request.user)    
    return render(request, 'consultas_sociales/ver_consulta_personal.html', {
        'consulta': consulta
    })




# ==========================================================
# 4. VISTAS DE RECLAMOS MUNICIPALES
# ==========================================================

@login_required
def crear_reclamo(request):
    """
    Permite a cualquier ciudadano logueado enviar un reclamo.
    """
    op = getattr(request.user, 'operador', None)
    if op and not op.operador_activo:
        logout(request)
        messages.error(request, "Cuenta desactivada.")
        return redirect('login')

    if request.method == 'POST':
        form = ReclamoForm(request.POST)
        if form.is_valid():
            reclamo = form.save(commit=False)
            reclamo.usuario = request.user
            reclamo.save()
            
            registrar_historial(
                request.user, 
                "CREAR", 
                "RECLAMOS", 
                f"Reclamo enviado a {reclamo.area_destino.nombre}: {reclamo.asunto}", 
                reclamo.id_reclamo
            )
            
            messages.success(request, "Su reclamo ha sido registrado. El área correspondiente trabajará en una solución.")
            return redirect('social:mis_reclamos') # O la vista que prefieras de inicio
    else:
        form = ReclamoForm()
    
    return render(request, 'reclamos/crear_reclamo.html', {'form': form})

@login_required
def lista_reclamos(request):
    """
    SOLO OPERADORES: Gestión de reclamos dirigidos a su área.
    """
    op = getattr(request.user, 'operador', None)
    
    if not op or not op.operador_activo or not op.area:
        raise PermissionDenied

    # Filtramos reclamos no respondidos de su área
    queryset = Reclamo.objects.filter(
        area_destino=op.area, 
        respondido=False
    ).order_by('-fecha_envio')

    # Buscador
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(asunto__icontains=query) | Q(usuario__username__icontains=query)
        )
    
    fecha_filtro = request.GET.get('fecha_filtro')
    if fecha_filtro:
        queryset = queryset.filter(fecha_envio__date=fecha_filtro)

    paginator = Paginator(queryset, 10)
    reclamos = paginator.get_page(request.GET.get('page'))

    return render(request, 'reclamos/lista_reclamos.html', {
        'reclamos': reclamos, 
        'query': query,
        'fecha_filtro': fecha_filtro
    })

@login_required
def ver_reclamo(request, id_reclamo):
    """
    OPERADOR: Ver detalle y dar resolución al reclamo.
    """
    op = getattr(request.user, 'operador', None)
    if op and not op.operador_activo:
        logout(request)
        return redirect('login')

    # Verificamos que sea operador de esa área
    reclamo = get_object_or_404(Reclamo, id_reclamo=id_reclamo, area_destino=op.area)

    if request.method == 'POST':
        form = RespuestaReclamoForm(request.POST, instance=reclamo)
        if form.is_valid():
            reclamo_resp = form.save(commit=False)
            reclamo_resp.respondido = True
            reclamo_resp.fecha_respuesta = timezone.now()
            reclamo_resp.save()
            
            registrar_historial(request.user, "EDITAR", "RECLAMOS", 
                              f"Resolvió reclamo: {reclamo.asunto}", id_reclamo)
            
            messages.success(request, "La resolución del reclamo ha sido enviada.")
            return redirect('social:lista_reclamos')
    else:
        form = RespuestaReclamoForm(instance=reclamo)

    return render(request, 'reclamos/ver_reclamo.html', {
        'reclamo': reclamo,
        'form': form
    })

@login_required
def borrar_logico_reclamo(request, id_reclamo):
    """
    Archiva el reclamo sin respuesta detallada (Cierre administrativo).
    """
    op = getattr(request.user, 'operador', None)
    if not op or not op.operador_activo:
        raise PermissionDenied

    reclamo = get_object_or_404(Reclamo, id_reclamo=id_reclamo, area_destino=op.area)
    
    if request.method == 'POST':
        reclamo.respondido = True
        reclamo.save()
        registrar_historial(request.user, "ELIMINAR", "RECLAMOS", f"Cerró reclamo (archivo): {reclamo.asunto}", id_reclamo)
        messages.warning(request, "El reclamo ha sido archivado.")
    
    return redirect('social:lista_reclamos')

@login_required
def mis_reclamos(request):
    """
    VECINO: Ver el historial de sus propios reclamos realizados.
    """
    reclamos = Reclamo.objects.filter(usuario=request.user).order_by('-fecha_envio')
    
    return render(request, 'reclamos/mis_reclamos.html', {
        'reclamos': reclamos,
    })

@login_required
def ver_reclamo_personal(request, id_reclamo):
    """
    VECINO: Ver el ticket de su reclamo y la respuesta (solo lectura).
    """
    reclamo = get_object_or_404(Reclamo, id_reclamo=id_reclamo, usuario=request.user)    
    return render(request, 'reclamos/ver_reclamo_personal.html', {
        'reclamo': reclamo
    })