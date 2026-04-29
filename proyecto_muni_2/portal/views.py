from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from django.db import transaction # Importante para la seguridad de los datos
# Modelos y Forms
from .models import Noticia, Eventos, Contacto, ComponenteSector, NotaRecordatorio, ArchivadorImagen
from .forms import EventoForm, ContactoForm, NoticiaForm, ConfiguracionSectorForm,NotaRecordatorioForm, ImagenNotaFormSet
from .utils import registrar_historial
from users.models import Area, Puesto, OperadorMunicipal, RolMunicipal
from users.decorators import tiene_permiso

# ==========================================================
# UTILS / HELPERS DE SEGURIDAD
# ==========================================================

def _verificar_operador_activo(request):
    """
    Expulsa al usuario si su perfil de operador está desactivado.
    """
    if request.user.is_superuser:
        return True
    op = getattr(request.user, 'operador', None)
    if op:
        if not op.operador_activo:
            logout(request)
            messages.error(request, "Su cuenta de operador ha sido desactivada.")
            return False
        return True
    return False

def _puede_gestionar(user, objeto):
    """Valida si el usuario tiene permiso sobre un objeto específico."""
    if user.is_superuser: return True
    op = getattr(user, 'operador', None)
    return op and op.operador_activo and objeto.area_id == op.area_id

def _es_operador_o_admin(user):
    """Verifica existencia y estado del operador."""
    if user.is_superuser: return True
    op = getattr(user, 'operador', None)
    return op is not None and op.operador_activo

# ==========================================================
# SECCIÓN: INICIO Y PÁGINAS INSTITUCIONALES
# ==========================================================

def bienvenida(request):
    """Página de aterrizaje: Muestra las últimas 12 noticias activas."""
    noticias = Noticia.objects.filter(activo=True).order_by('-id_noticia')[:12]
    return render(request, 'portal/bienvenida.html', {'noticias': noticias})

def lista_servicios(request): return render(request, 'portal/lista_servicios.html')
def informacion(request): return render(request, 'portal/informacion.html')
def autoridades_view(request): return render(request, "portal/autoridades.html")
def historia(request): return render(request, 'portal/historia.html')
def intendencias(request): return render(request, "portal/intendencias.html")
def organigrama(request): return render(request, "portal/organigrama.html")
def sectores_municipales(request): return render(request, "portal/sectores_municipales.html")


# ==========================================================
# SECCIÓN: NOTICIAS
# ==========================================================

# --- Vistas Públicas ---
def lista_noticias_publica(request):
    noticias_list = Noticia.objects.filter(activo=True).order_by('-id_noticia')

    query_titulo = request.GET.get('titulo')
    query_fecha = request.GET.get('fecha')
    query_area = request.GET.get('area')

    # 🔍 FILTROS
    if query_titulo:
        noticias_list = noticias_list.filter(titulo__icontains=query_titulo)

    if query_fecha:
        try:
            fecha = datetime.strptime(query_fecha, "%Y-%m-%d").date()
            noticias_list = noticias_list.filter(fecha_creacion__date=fecha)
        except (ValueError, TypeError):
            pass

    # FILTRO AREA - Cambiado de area__id a area__id_area
    if query_area and query_area.isdigit():
        noticias_list = noticias_list.filter(area__id_area=query_area)

    # PAGINACION
    paginator = Paginator(noticias_list, 8)
    page = request.GET.get('page')
    noticias = paginator.get_page(page)

    return render(request, 'portal/noticias/noticias_publicas.html', {
        'noticias': noticias,
        'areas': Area.objects.all(),
        # Agregamos estas variables para que el HTML reconozca el estado actual
        'area_actual': query_area, 
    })


def ver_noticia_publica(request, slug):
    noticia = get_object_or_404(Noticia, slug=slug, activo=True)
    return render(request, 'portal/noticias/detalle_noticia.html', {'noticia': noticia})

@login_required
def gestion_noticias(request):
    if not _verificar_operador_activo(request): 
        return redirect('login')
    return render(request, 'portal/noticias/gestion_noticias.html')


# --- Gestión de Noticias (Operadores) ---
@login_required
def panel_operador_noticias(request):
    if not _verificar_operador_activo(request): 
        return redirect('login')
    
    op = request.user.operador
    
    # 1. Filtro base según permisos
    if request.user.is_superuser or (op.rol in [RolMunicipal.SUPER_USUARIO, RolMunicipal.ADMINISTRADOR]):
        noticias_list = Noticia.objects.all()
    else:
        noticias_list = Noticia.objects.filter(area=op.area)

    # 2. Procesar Buscadores (Filtros GET)
    titulo = request.GET.get('titulo')
    area_id = request.GET.get('area')
    fecha = request.GET.get('fecha')

    if titulo:
        noticias_list = noticias_list.filter(titulo__icontains=titulo)
    
    if area_id:
        noticias_list = noticias_list.filter(area_id=area_id)
        
    if fecha:
    # Usamos fecha_creacion__date para comparar solo la fecha sin la hora
        noticias_list = noticias_list.filter(fecha_creacion__date=fecha)
    
    # 3. Orden y Paginación (8 datos por página)
    noticias_list = Noticia.objects.filter(activo=True).order_by('-fecha_creacion')
    paginator = Paginator(noticias_list, 8) # Cambiado de 15 a 8
    
    page_number = request.GET.get('page')
    noticias = paginator.get_page(page_number)
    
    return render(request, 'portal/noticias/panel_operador.html', {
        'noticias': noticias,
        'areas': Area.objects.all()
    })


@login_required
def panel_operador_desactivadas(request):
    if not _verificar_operador_activo(request): 
        return redirect('login')
    
    op = request.user.operador
    
    # 1. Filtro base según permisos
    if request.user.is_superuser or (op.rol in [RolMunicipal.SUPER_USUARIO, RolMunicipal.ADMINISTRADOR]):
        noticias_list = Noticia.objects.all()
    else:
        noticias_list = Noticia.objects.filter(area=op.area)

    # 2. Procesar Buscadores (Filtros GET)
    titulo = request.GET.get('titulo')
    area_id = request.GET.get('area')
    fecha = request.GET.get('fecha')

    if titulo:
        noticias_list = noticias_list.filter(titulo__icontains=titulo)
    
    if area_id:
        noticias_list = noticias_list.filter(area_id=area_id)
        
    if fecha:
    # Usamos fecha_creacion__date para comparar solo la fecha sin la hora
        noticias_list = noticias_list.filter(fecha_creacion__date=fecha)
    
    # 3. Orden y Paginación (8 datos por página)
    noticias_list = Noticia.objects.filter(activo=False).order_by('-fecha_creacion')
    paginator = Paginator(noticias_list, 8) # Cambiado de 15 a 8
    
    page_number = request.GET.get('page')
    noticias = paginator.get_page(page_number)
    
    return render(request, 'portal/noticias/panel_operador_desactivadas.html', {
        'noticias': noticias,
        'areas': Area.objects.all()
    })


@login_required
def crear_noticia(request):
    if not _verificar_operador_activo(request): 
        return redirect('login')
    
    op = getattr(request.user, 'operador', None)
    
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES)
        if form.is_valid():
            noticia = form.save(commit=False)
            if op:
                noticia.autor = op
                noticia.area = op.area
                noticia.save()
                registrar_historial(request.user, "CREAR", "NOTICIAS", f"Noticia: {noticia.titulo}", noticia.id_noticia)
                messages.success(request, "Noticia creada exitosamente.")
                return redirect('panel_operador_noticias')
        else:
            # Si el formulario falla, esto te dirá por qué en la consola
            print(form.errors) 
    else:
        form = NoticiaForm()
        
    return render(request, 'portal/noticias/form_noticia.html', {'form': form})

@login_required
def editar_noticia(request, id_noticia):
    if not _verificar_operador_activo(request): return redirect('login')
    
    noticia = get_object_or_404(Noticia, pk=id_noticia)
    if not _puede_gestionar(request.user, noticia):
        messages.error(request, "No tienes permiso para editar esta noticia.")
        return redirect('panel_operador_noticias')

    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES, instance=noticia)
        if form.is_valid():
            form.save()
            registrar_historial(request.user, "EDITAR", "NOTICIAS", f"Editó: {noticia.titulo}", noticia.id_noticia)
            messages.success(request, "Noticia actualizada.")
            return redirect('panel_operador_noticias')
    else:
        form = NoticiaForm(instance=noticia)
    return render(request, 'portal/noticias/form_noticia.html', {'form': form, 'noticia': noticia})

@login_required
def eliminar_noticia(request, id_noticia):
    if not _verificar_operador_activo(request): return redirect('login')
    
    noticia = get_object_or_404(Noticia, pk=id_noticia)
    if not _puede_gestionar(request.user, noticia): raise PermissionDenied
    if request.method == 'POST':
        noticia.activo = False
        noticia.save()
        registrar_historial(request.user, "ELIMINAR", "NOTICIAS", f"Baja lógica: {noticia.titulo}", id_noticia)
        return redirect('panel_operador_noticias')
    return render(request, 'portal/noticias/confirmar_eliminar.html', {'noticia': noticia})


# ==========================================================
# SECCIÓN: CONTACTOS
# ==========================================================

# --- Vistas Públicas ---
def contactos(request):
    """Guía de contactos municipal para el vecino."""
    contactos_list = Contacto.objects.filter(activo=True).select_related('area', 'puesto').order_by('nombre_completo')
    query = request.GET.get('search')
    area_id = request.GET.get('area')
    
    if query: contactos_list = contactos_list.filter(Q(nombre_completo__icontains=query) | Q(puesto__nombre__icontains=query))
    if area_id: contactos_list = contactos_list.filter(area_id=area_id)

    paginator = Paginator(contactos_list, 8)
    contactos = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'portal/contacto/contactos.html', {
        'contactos': contactos,
        'opciones_areas': Area.objects.all().order_by('nombre')
    })

def ver_contacto(request, contacto_id):
    contacto = get_object_or_404(Contacto, id_contacto=contacto_id, activo=True)
    return render(request, "portal/contacto/ver_contacto.html", {"contacto": contacto})

# ==========================================================
# SECCIÓN: CONTACTOS (GESTIÓN RESTRINGIDA POR ÁREA)
# ==========================================================

@login_required
def crear_contacto(request):
    """
    Los operadores solo crean contactos para su propia área.
    """
    if not _verificar_operador_activo(request): 
        return redirect('login')
    
    op = getattr(request.user, 'operador', None)
    
    if request.method == 'POST':
        # Pasamos el usuario al form para que valide el área internamente
        form = ContactoForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            contacto = form.save(commit=False)
            contacto.creado_por = request.user
            
            # Forzamos el área del operador (si no es superuser)
            if not request.user.is_superuser and op:
                contacto.area = op.area
            
            contacto.save()
            registrar_historial(request.user, "CREAR", "CONTACTOS", f"Contacto: {contacto.nombre_completo}", contacto.id_contacto)
            messages.success(request, "Contacto guardado correctamente.")
            return redirect('contactos')
    else:
        # El form debe recibir el user para filtrar los Puestos de su área
        form = ContactoForm(user=request.user)
        
    return render(request, 'portal/contacto/crear_contacto.html', {'form': form})

@login_required
def editar_contacto(request, contacto_id):
    """
    Solo permite editar si el contacto pertenece al área del operador.
    """
    if not _verificar_operador_activo(request): 
        return redirect('login')
    
    contacto = get_object_or_404(Contacto, id_contacto=contacto_id)
    
    # VALIDACIÓN DE ÁREA: Si no es de su área, rebota
    if not _puede_gestionar(request.user, contacto):
        messages.error(request, "Acceso denegado: Este contacto pertenece a otra área y no puedes modificarlo.")
        return redirect('contactos')

    if request.method == 'POST':
        form = ContactoForm(request.POST, request.FILES, instance=contacto, user=request.user)
        if form.is_valid():
            contacto = form.save(commit=False)
            contacto.ultima_modificacion_por = request.user
            contacto.save()
            registrar_historial(request.user, "EDITAR", "CONTACTOS", f"Actualizó: {contacto.nombre_completo}", contacto.id_contacto)
            messages.success(request, "Contacto actualizado exitosamente.")
            return redirect('contactos')
    else:
        form = ContactoForm(instance=contacto, user=request.user)
        
    return render(request, 'portal/contacto/editar_contacto.html', {'form': form, 'contacto': contacto})

@login_required
def eliminar_contacto(request, contacto_id):
    """
    Solo permite dar de baja si el contacto pertenece al área del operador.
    """
    if not _verificar_operador_activo(request): 
        return redirect('login')
    
    contacto = get_object_or_404(Contacto, id_contacto=contacto_id)
    
    # VALIDACIÓN DE ÁREA
    if not _puede_gestionar(request.user, contacto):
        messages.error(request, "No tienes permisos para eliminar contactos de otras áreas.")
        return redirect('contactos')
    
    if request.method == 'POST':
        contacto.activo = False
        contacto.save()
        registrar_historial(request.user, "ELIMINAR", "CONTACTOS", f"Baja: {contacto.nombre_completo}", contacto.id_contacto)
        messages.warning(request, "El contacto ha sido desactivado.")
        return redirect('contactos')
        
    # Si intentan entrar por GET a eliminar, redirigimos
    return redirect('contactos')

# ==========================================================
# SECCIÓN: EVENTOS
# ==========================================================

# --- Vistas Públicas ---
def eventos(request):
    eventos = Eventos.objects.filter(activo=True).order_by('-fecha')
    return render(request, "portal/evento/eventos.html", {"eventos": eventos})

# --- Gestión de Eventos (Solo ADMIN_GRAL) ---
@login_required
@tiene_permiso('ADMIN_GRAL')
def crear_evento(request):
    if not _verificar_operador_activo(request): return redirect('login')
    
    op = getattr(request.user, 'operador', None)
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.user = request.user
            if op: evento.area = op.area
            evento.save()
            registrar_historial(request.user, "CREAR", "EVENTOS", f"Evento: {evento.titulo}", evento.id_evento)
            messages.success(request, "Evento creado.")
            return redirect('eventos')
    else:
        form = EventoForm()
    return render(request, 'portal/evento/crear_evento.html', {'form': form})

@login_required
@tiene_permiso('ADMIN_GRAL')
def editar_evento(request, id_evento):
    if not _verificar_operador_activo(request): return redirect('login')
    
    evento = get_object_or_404(Eventos, pk=id_evento)
    if not _puede_gestionar(request.user, evento):
        messages.error(request, "Este evento pertenece a otra área.")
        return redirect('eventos')

    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            form.save()
            registrar_historial(request.user, "EDITAR", "EVENTOS", f"Editó: {evento.titulo}", evento.id_evento)
            messages.success(request, "Evento actualizado.")
            return redirect('eventos')
    else:
        form = EventoForm(instance=evento)
    return render(request, 'portal/evento/editar_evento.html', {'form': form, 'evento': evento})

@login_required
@tiene_permiso('ADMIN_GRAL')
def eliminar_evento(request, id_evento):
    if not _verificar_operador_activo(request): return redirect('login')
    
    if request.method == 'POST':
        evento = get_object_or_404(Eventos, pk=id_evento)
        if not _puede_gestionar(request.user, evento): raise PermissionDenied
        evento.activo = False
        evento.save()
        registrar_historial(request.user, "ELIMINAR", "EVENTOS", f"Eliminó: {evento.titulo}", id_evento)
        messages.success(request, "Evento eliminado.")
    return redirect('eventos')


# ==========================================================
# SECCIÓN: HELPERS AJAX / DINÁMICOS
# ==========================================================

def ajax_load_puestos(request):
    """Carga puestos dinámicamente según el área seleccionada."""
    area_id = request.GET.get('area_id')
    puestos = Puesto.objects.filter(area_id=area_id).order_by('nombre')
    return render(request, 'portal/contacto/ajax_load_puestos.html', {'puestos': puestos})



# Vistas sobre Notas y Configuración de Sector se encuentran en views_notas.py para mantener este archivo más limpio.
@login_required
def lista_notas(request):
    # Traemos solo las notas del usuario logueado que no fueron "borradas"
    notas = NotaRecordatorio.objects.filter(usuario=request.user, activo=True).order_by('-fecha_actual')
    
    return render(request, 'portal/notas/lista_notas.html', {
        'notas': notas
    })

@login_required
def crear_nota_recordatorio(request):
    if request.method == 'POST':
        form = NotaRecordatorioForm(request.POST)
        formset = ImagenNotaFormSet(request.POST, request.FILES, prefix='imagenes')
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # Guardamos la nota
                    nota = form.save(commit=False)
                    nota.usuario = request.user
                    nota.save()
                    
                    # Vinculamos y guardamos el formset
                    formset.instance = nota
                    formset.save()
                
                messages.success(request, "Recordatorio guardado correctamente.")
                return redirect('lista_notas')
            except Exception as e:
                messages.error(request, f"Hubo un error al guardar: {e}")
    else:
        form = NotaRecordatorioForm()
        formset = ImagenNotaFormSet(prefix='imagenes')
    
    return render(request, 'portal/notas/crear_nota.html', {
        'form': form, 
        'formset': formset
    })

@login_required
def editar_nota_recordatorio(request, pk):
    # Usamos activo=True para respetar tu borrado lógico
    nota = get_object_or_404(NotaRecordatorio, pk=pk, usuario=request.user, activo=True)
    
    if request.method == 'POST':
        form = NotaRecordatorioForm(request.POST, instance=nota)
        formset = ImagenNotaFormSet(request.POST, request.FILES, instance=nota, prefix='imagenes')
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    formset.save()
                messages.success(request, "Nota actualizada con éxito.")
                return redirect('lista_notas')
            except Exception as e:
                messages.error(request, f"Error al actualizar: {e}")
    else:
        form = NotaRecordatorioForm(instance=nota)
        formset = ImagenNotaFormSet(instance=nota, prefix='imagenes')
    
    return render(request, 'portal/notas/editar_nota.html', {
        'form': form, 
        'formset': formset, 
        'nota': nota
    })

@login_required
def ver_nota_recordatorio(request, pk):
    nota = get_object_or_404(
        NotaRecordatorio,
        pk=pk,
        usuario=request.user,
        activo=True
    )

    return render(request, 'portal/notas/ver_nota.html', {
        'nota': nota
    })

@login_required
def eliminar_nota_logico(request, pk):
    # Borrado lógico: cambiamos el estado, no borramos la fila de la DB
    nota = get_object_or_404(NotaRecordatorio, pk=pk, usuario=request.user)
    nota.activo = False
    nota.save()
    messages.success(request, "Nota movida al archivador (borrado lógico).")
    return redirect('lista_notas')