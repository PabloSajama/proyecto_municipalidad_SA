from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User, Group
from django.http import HttpResponseForbidden
from django.contrib import messages
from .forms import *
from .models import *
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime, time
from .utils import solo_super_autorizados
from django.core.exceptions import PermissionDenied
from functools import wraps



# --- 1. FUNCIONES DE VERIFICACIÓN (Lógica de Negocio) ---

def es_administrador(user, area_objetivo=None):
    """Verifica si es Superusuario o tiene grupo 'Administrador' en el área correcta."""
    if not user.is_authenticated: return False
    if user.is_superuser: return True
    
    tiene_grupo_admin = user.groups.filter(name='Administrador').exists()
    if not tiene_grupo_admin: return False
    
    if area_objetivo is None: return True
    # Acceso total si su área coincide o si es Administrador General
    return user.perfil.area == area_objetivo or user.perfil.area == 'ADMIN_GRAL'

def es_operador(user, area_objetivo=None):
    """Verifica si tiene grupo 'Operador' en el área correcta."""
    if not user.is_authenticated: return False
    # Por jerarquía, un Administrador también puede realizar tareas de Operador
    if es_administrador(user, area_objetivo): return True
    
    tiene_grupo_operador = user.groups.filter(name='Operador').exists()
    if not tiene_grupo_operador: return False
    
    if area_objetivo is None: return True
    return user.perfil.area == area_objetivo or user.perfil.area == 'ADMIN_GRAL'

def es_personal(user, area_objetivo=None):
    """Verifica si el usuario es trabajador del área (ya sea Admin u Operador)."""
    return es_administrador(user, area_objetivo) or es_operador(user, area_objetivo)


# --- 2. DECORADORES DE SEGURIDAD (Protección de Vistas) ---

def solo_super_autorizados(view_func):
    """Acceso exclusivo al Panel Maestro para usernames específicos."""
    @wraps(view_func)
    def _wrapped_view_func(request, *args, **kwargs):
        autorizados = ['administracion_prueba', 'director_sociales']
        if request.user.is_authenticated and request.user.username in autorizados:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view_func

def tiene_permiso(area_objetivo, solo_admin=False):
    """
    Decorador Universal:
    - area_objetivo: El área a la que pertenece la vista (CATASTRO, COMERCIO, etc.)
    - solo_admin: Si es True, solo permite el paso al grupo Administrador.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if user.is_superuser:
                return view_func(request, *args, **kwargs)

            if solo_admin:
                if es_administrador(user, area_objetivo):
                    return view_func(request, *args, **kwargs)
            else:
                if es_personal(user, area_objetivo):
                    return view_func(request, *args, **kwargs)
            
            raise PermissionDenied
        return _wrapped_view
    return decorator



# --- 3. GESTIÓN DE ROLES Y ÁREAS (Panel Maestro) ---

@login_required
@solo_super_autorizados
def gestionar_roles(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        nueva_area = request.POST.get('area')
        nuevo_rol = request.POST.get('rol') # 'Administrador', 'Operador' o 'invitado'
        
        usuario = get_object_or_404(User, id=user_id)
        perfil, _ = Perfil.objects.get_or_create(user=usuario)
        
        # 1. Actualizamos el Área en el Perfil
        perfil.area = nueva_area
        perfil.save()
        
        # 2. Actualizamos el Rol (Grupos de Django)
        usuario.groups.clear()
        if nuevo_rol == 'invitado':
            usuario.is_staff = False
            # El área VISITANTE no da permisos de edición
        else:
            grupo, _ = Group.objects.get_or_create(name=nuevo_rol)
            usuario.groups.add(grupo)
            usuario.is_staff = True # Permite acceso a herramientas internas
        
        usuario.save()
        messages.success(request, f"Permisos actualizados para {usuario.username}")
        return redirect('gestionar_roles')

    usuarios = User.objects.all().select_related('perfil').order_by('username')
    areas_disponibles = Perfil.AREAS_CHOICES 
    
    return render(request, 'admin_custom/gestionar_roles.html', {
        'usuarios': usuarios,
        'areas_disponibles': areas_disponibles
    })


# Vistas Errores

def error_403(request, exception):
    return render(request, '403.html', status=403)

def error_500(request):
    return render(request, '500.html', status=500)


# vista inicio
def bienvenida(request):
    noticias = (
        Noticia.objects
        .filter(activo=True)
        .order_by('-id_noticia')[:8]  # 🔴 SOLO 8
    )
    return render(request, 'bienvenida.html', {'noticias': noticias})


def lista_servicios(request):
    return render(request, 'lista_servicios.html')

def informacion(request):
    return render(request, 'informacion.html')


# Rentas
def renta_info(request):
    return render(request, 'rentas.html')

def tasas_municipales(request):
    return render(request, "tasas.html")

def regularizaciones(request):
    return render(request, "regularizaciones.html")


# quienes somos
def autoridades_view(request):
    return render(request, "autoridades/autoridades.html")

def historia(request):
    return render(request, 'autoridades/historia.html')

def intendencias(request):
    return render(request, "autoridades/intendencias.html")

def organigrama(request):
    return render(request, "autoridades/organigrama.html")



# Noticias
@login_required
@user_passes_test(es_personal) 
def crear_noticia(request):
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES)
        if form.is_valid():
            noticia = form.save(commit=False)
            noticia.user = request.user
            noticia.save()
            messages.success(request, f'Noticia "{noticia.titulo}" creada con éxito en el sector {noticia.get_sector_display()}.')
            return redirect('lista_noticias')
    else:
        form = NoticiaForm()
    return render(request, 'noticias/crear_noticia.html', {'form': form})

def lista_noticias(request):
    # 1. Obtenemos noticias activas
    noticias_list = Noticia.objects.filter(activo=True).order_by('-id_noticia')
    
    # 2. Obtenemos el sector desde la URL (ej: ?sector=SOCIAL)
    sector_slug = request.GET.get('sector')
    if sector_slug:
        noticias_list = noticias_list.filter(sector=sector_slug)

    # 3. Paginación
    paginator = Paginator(noticias_list, 10) 
    page_number = request.GET.get('page')
    noticias_paginadas = paginator.get_page(page_number)

    # 4. PASAR OPCIONES DEL MODELO AL TEMPLATE
    # Noticia._meta.get_field('sector').choices obtiene la lista SECTORES_CHOICES
    opciones_sectores = Noticia._meta.get_field('sector').choices

    return render(request, 'noticias/lista_noticias.html', {
        'noticias': noticias_paginadas,
        'sector_actual': sector_slug,
        'opciones_sectores': opciones_sectores  # <--- Esto es lo nuevo
    })

@login_required
@user_passes_test(es_personal) 
def editar_noticia(request, id_noticia):
    noticia = get_object_or_404(Noticia, pk=id_noticia)
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES, instance=noticia)
        if form.is_valid():
            # Manejo de limpieza de imagen si el usuario marcó el checkbox
            if request.POST.get('imagen_principal-clear') == 'on':
                if noticia.imagen_principal:
                    noticia.imagen_principal.delete(save=False)
                noticia.imagen_principal = None
            
            form.save()
            messages.success(request, 'Noticia actualizada correctamente.')
            return redirect('lista_noticias')
    else:
        form = NoticiaForm(instance=noticia)
    return render(request, 'noticias/editar_noticia.html', {'form': form, 'noticia': noticia})

@login_required
@user_passes_test(es_administrador) 
def eliminar_noticia(request, id_noticia):
    # Usamos borrado lógico (cambiar activo a False) por seguridad
    if request.method == 'POST':
        noticia = get_object_or_404(Noticia, pk=id_noticia)
        noticia.activo = False
        noticia.save()
        messages.warning(request, 'La noticia ha sido desactivada.')
        return redirect('lista_noticias')
    return HttpResponseForbidden()

def ver_noticia(request, id_noticia):
    # Solo permitimos ver noticias que estén activas
    noticia = get_object_or_404(Noticia, id_noticia=id_noticia, activo=True)
    return render(request, 'noticias/ver_noticia.html', {'noticia': noticia})


# Vistas para autenticación
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario registrado con éxito. Ya puedes iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'inicio/registro.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            return redirect('bienvenida')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    return render(request, 'inicio/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')


# --- Vistas para Catastro ---

# 1. Info pública: No lleva decoradores (todos pueden verla)
def catastro_info(request):
    return render(request, 'catastros/catastro.html')

# 2. Listar: Solo personal de Catastro (Admin u Operador)
@login_required
@tiene_permiso('CATASTRO') 
def listar_catastros(request):
    queryset = Catastros.objects.filter(eliminado=False)
    dni = request.GET.get('dni')
    numero = request.GET.get('numero')
    nombre = request.GET.get('nombre')

    if dni: queryset = queryset.filter(dni_propietario__icontains=dni)
    if numero: queryset = queryset.filter(numero_catastro__icontains=numero)
    if nombre: queryset = queryset.filter(nombre_propietario__icontains=nombre)

    return render(request, 'catastros/listar_catastros.html', {
        'catastros': queryset,
        'dni': dni, 'numero': numero, 'nombre': nombre,
    })

# 3. Crear: Solo personal de Catastro
@login_required
@tiene_permiso('CATASTRO') 
def crear_catastro(request):
    if request.method == 'POST':
        form = CatastroForm(request.POST, request.FILES)
        if form.is_valid():
            catastro = form.save(commit=False)
            catastro.eliminado = False
            catastro.save()
            messages.success(request, "Registro creado con éxito.")
            return redirect('listar_catastros')
    else:
        form = CatastroForm()
    return render(request, 'catastros/crear_catastro.html', {'form': form})

# 4. Ver Detalle: Solo personal de Catastro
@login_required
@tiene_permiso('CATASTRO') 
def ver_catastro(request, id_catastro):
    catastro = get_object_or_404(Catastros, id_catastro=id_catastro, eliminado=False)
    return render(request, 'catastros/ver_catastro.html', {'catastro': catastro})

# 5. Editar: Solo personal de Catastro
@login_required
@tiene_permiso('CATASTRO') 
def editar_catastro(request, id_catastro):
    catastro = get_object_or_404(Catastros, id_catastro=id_catastro, eliminado=False)
    if request.method == 'POST':
        form = CatastroForm(request.POST, request.FILES, instance=catastro)
        if form.is_valid():
            form.save()
            messages.success(request, "Registro actualizado.")
            return redirect('listar_catastros')
    else:
        form = CatastroForm(instance=catastro)
    return render(request, 'catastros/editar_catastro.html', {
        'form': form,
        'catastro': catastro
    })

# 6. Eliminar: EXCLUSIVO para el Administrador de Catastro
@login_required
@tiene_permiso('CATASTRO', solo_admin=True) 
def eliminar_catastro(request, id_catastro):
    if request.method == 'POST':
        catastro = get_object_or_404(Catastros, id_catastro=id_catastro, eliminado=False)
        catastro.eliminado = True
        catastro.save()
        messages.warning(request, "El registro ha sido eliminado.")
        return redirect('listar_catastros')
    return HttpResponseForbidden("Acción no permitida por este medio.")


# Eventos
def eventos(request):
    eventos = Eventos.objects.filter(activo=True)
    return render(request, "eventos/eventos.html", {"eventos": eventos})

@login_required
@user_passes_test(es_personal) # Admin y Operador pueden crear
def crear_evento(request):
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.user = request.user
            evento.fecha_publicacion = timezone.now().date()
            evento.save()
            return redirect('eventos')
    else:
        form = EventoForm()
    return render(request, 'eventos/crear_evento.html', {'form': form})

@login_required
@user_passes_test(es_personal) # Admin y Operador pueden editar
def editar_evento(request, id_evento):
    evento = get_object_or_404(Eventos, pk=id_evento)
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            return redirect('eventos')
    else:
        form = EventoForm(instance=evento)
    return render(request, 'eventos/editar_evento.html', {'form': form, 'evento': evento})

@login_required
@user_passes_test(es_administrador) # Solo Admin puede eliminar evento
def eliminar_evento(request, id_evento):
    evento = get_object_or_404(Eventos, pk=id_evento)
    evento.activo = False
    evento.save()
    return redirect('eventos')





# Vistas de Eventos Sociales

def eventos_sociales(request):
    eventos = EventosSociales.objects.filter(
        activo=True
    ).order_by('fecha_evento')

    return render(
        request,
        "eventos_sociales/eventos_sociales.html",
        {"eventos": eventos}
    )


# CREAR
@login_required
@user_passes_test(es_personal)
def crear_evento_social(request):
    if request.method == 'POST':
        form = EventoSocialForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            
            # Extraemos los campos del formulario
            fecha_selec = form.cleaned_data['fecha']
            hora_selec_str = form.cleaned_data['hora']
            
            # Convertimos string a objeto time
            hora_obj = datetime.strptime(hora_selec_str, '%H:%M').time()
            
            # UNIMOS usando la clase datetime.combine
            evento.fecha_evento = datetime.combine(fecha_selec, hora_obj)
            
            evento.user = request.user
            evento.save()
            return redirect('eventos_sociales')
    else:
        form = EventoSocialForm()

    return render(
        request,
        'eventos_sociales/crear_evento_social.html',
        {'form': form}
    )


# EDITAR
@login_required
@user_passes_test(es_personal)
def editar_evento_social(request, id_social):
    evento = get_object_or_404(EventosSociales, pk=id_social)

    if request.method == 'POST':
        form = EventoSocialForm(
            request.POST,
            request.FILES,
            instance=evento
        )
        if form.is_valid():
            evento_editado = form.save(commit=False)
            
            # Repetimos la lógica de unión para capturar cambios en fecha u hora
            fecha_selec = form.cleaned_data['fecha']
            hora_selec_str = form.cleaned_data['hora']
            
            hora_obj = datetime.strptime(hora_selec_str, '%H:%M').time()
            
            # Actualizamos el campo fecha_evento del modelo
            evento_editado.fecha_evento = datetime.combine(fecha_selec, hora_obj)
            
            evento_editado.save()
            return redirect('eventos_sociales')
    else:
        # El __init__ del form se encarga de separar la fecha_evento original 
        # en los campos 'fecha' y 'hora' para que aparezcan rellenos al editar.
        form = EventoSocialForm(instance=evento)

    return render(
        request,
        'eventos_sociales/editar_evento_social.html',
        {
            'form': form,
            'evento': evento
        }
    )


# ELIMINAR (soft delete)
@login_required
@user_passes_test(es_administrador)  # SOLO Admin
def eliminar_evento_social(request, id_social):
    evento = get_object_or_404(EventosSociales, pk=id_social)
    evento.activo = False
    evento.save()
    return redirect('eventos_sociales')





# Consultas Sociales
@login_required
def crear_consulta(request):
    if request.method == "POST":
        asunto = request.POST.get("asunto")
        mensaje = request.POST.get("mensaje")
        consulta = ConsultasSociales(
            user = request.user,
            asunto = asunto,
            mensaje = mensaje,
            fecha_envio = timezone.now(),
        )
        consulta.save()
        return redirect('consultas')
    else:
        return render(request, "consultas/consultas.html")
    
@login_required
@user_passes_test(es_personal) # Admin y Operador ven consultas
def ver_consultas(request):
    consultas = ConsultasSociales.objects.all().order_by('-fecha_envio')
    return render(request, "consultas/ver_consultas.html", {"consultas": consultas})

@login_required
@user_passes_test(es_administrador) # Solo Admin elimina consultas
def eliminar_consulta(request, id_consulta):
    if request.method == 'POST':
        consulta = get_object_or_404(ConsultasSociales, id_consulta=id_consulta)
        consulta.delete()
        return redirect('ver_consultas')
    else:
        return HttpResponseForbidden("Acción no permitida.")
    
@login_required
@user_passes_test(es_personal) # Admin y Operador ven detalle
def ver_consulta_individual(request, id_consulta):
    consulta = get_object_or_404(ConsultasSociales, pk=id_consulta)
    return render(request, "consultas/ver_consulta_individual.html", {"consulta": consulta})


# ver contactos

def obtener_area_mapeada(user):
    mapeo = {'SOCIAL': 'SOCIAL', 'RENTAS': 'HACIENDA', 'CATASTRO': 'CATASTRO'}
    return mapeo.get(user.perfil.area, 'GENERAL')

def puede_gestionar_contacto(user, contacto):
    if user.is_superuser:
        return True
    return contacto.area == obtener_area_mapeada(user)

def contactos(request):
    contactos_list = Contacto.objects.filter(activo=True).order_by('nombre_completo')
    
    query_nombre = request.GET.get('search')
    query_puesto = request.GET.get('puesto')
    area_slug = request.GET.get('area')

    if query_nombre: contactos_list = contactos_list.filter(nombre_completo__icontains=query_nombre)
    if query_puesto: contactos_list = contactos_list.filter(puesto__icontains=query_puesto)
    if area_slug: contactos_list = contactos_list.filter(area=area_slug)

    paginator = Paginator(contactos_list, 8)
    page_number = request.GET.get('page')
    contactos_paginados = paginator.get_page(page_number)

    return render(request, 'contactos/contactos.html', {
        'contactos': contactos_paginados,
        'query': query_nombre,
        'puesto_actual': query_puesto,
        'area_actual': area_slug,
        'opciones_areas': Contacto.AREAS_CHOICES
    })

def ver_contacto(request, contacto_id):
    contacto = get_object_or_404(Contacto, pk=contacto_id)
    # Incluimos el historial ordenado por fecha descendente
    historial = contacto.historial.all().order_by('-fecha')
    return render(request, "contactos/ver_contacto.html", {
        "contacto": contacto,
        "historial": historial
    })

@login_required
def crear_contacto(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            contacto = form.save(commit=False)
            # Auditoría y Seguridad
            contacto.creado_por = request.user
            if not request.user.is_superuser:
                contacto.area = obtener_area_mapeada(request.user)
            contacto.save()

            # Registro en Historial
            HistorialContacto.objects.create(
                contacto=contacto,
                usuario=request.user,
                accion='CREACIÓN',
                detalles=f"Contacto creado inicialmente por {request.user.username}"
            )

            messages.success(request, "Contacto creado exitosamente.")
            return redirect('contactos')
    else:
        form = ContactoForm(user=request.user)
    return render(request, 'contactos/crear_contacto.html', {'form': form})

@login_required
def editar_contacto(request, contacto_id):
    contacto = get_object_or_404(Contacto, pk=contacto_id)
    
    if not puede_gestionar_contacto(request.user, contacto):
        messages.error(request, "No puedes editar contactos de otras áreas.")
        return redirect('contactos')

    if request.method == 'POST':
        form = ContactoForm(request.POST, request.FILES, instance=contacto, user=request.user)
        if form.is_valid():
            contacto = form.save(commit=False)
            contacto.ultima_modificacion_por = request.user
            contacto.save()

            # Registro en Historial
            HistorialContacto.objects.create(
                contacto=contacto,
                usuario=request.user,
                accion='EDICIÓN',
                detalles=f"Datos actualizados por {request.user.username}"
            )

            messages.success(request, "Contacto actualizado.")
            return redirect('contactos')
    else:
        form = ContactoForm(instance=contacto, user=request.user)
    return render(request, 'contactos/editar_contacto.html', {'form': form, 'contacto': contacto})

@login_required
def eliminar_contacto(request, contacto_id):
    # Usamos id_contacto como definiste en tu modelo
    contacto = get_object_or_404(Contacto, id_contacto=contacto_id)
    
    if not puede_gestionar_contacto(request.user, contacto):
        messages.error(request, "No tienes permiso para desactivar este contacto.")
        return redirect('contactos')
    
    contacto.activo = False
    contacto.save()

    # Registro en Historial
    HistorialContacto.objects.create(
        contacto=contacto,
        usuario=request.user,
        accion='DESACTIVACIÓN',
        detalles=f"Contacto desactivado (borrado lógico) por {request.user.username}"
    )

    messages.success(request, "Contacto desactivado correctamente.")
    return redirect('contactos')

@login_required
def papelera_contactos(request):
    # Obtenemos solo los inactivos
    contactos_inactivos = Contacto.objects.filter(activo=False).order_by('-fecha_modificacion')

    # Si no es superadmin, solo ve los inactivos de su propia área
    if not request.user.is_superuser and request.user.perfil.area not in ['ADMIN_GRAL', 'SISTEMAS']:
        area_usuario = obtener_area_mapeada(request.user)
        contactos_inactivos = contactos_inactivos.filter(area=area_usuario)

    return render(request, 'contactos/papelera_contacto.html', {
        'contactos': contactos_inactivos
    })

@login_required
def restaurar_contacto(request, contacto_id):
    contacto = get_object_or_404(Contacto, id_contacto=contacto_id)
    
    # Validar que tenga permiso sobre esa área
    if not puede_gestionar_contacto(request.user, contacto):
        messages.error(request, "No tienes permiso para restaurar este contacto.")
        return redirect('papelera_contactos')

    contacto.activo = True
    contacto.save()

    # Registrar en historial
    HistorialContacto.objects.create(
        contacto=contacto,
        usuario=request.user,
        accion='RESTAURACIÓN',
        detalles=f"Contacto restaurado desde la papelera por {request.user.username}"
    )

    messages.success(request, f"El contacto '{contacto.nombre_completo}' ha sido restaurado.")
    return redirect('contactos')

@login_required
def eliminar_permanente_contacto(request, contacto_id):
    # Solo el Superusuario puede ejecutar esta acción
    if not request.user.is_superuser:
        messages.error(request, "Acceso denegado: Solo los superusuarios pueden borrar registros permanentemente.")
        return redirect('contactos')

    contacto = get_object_or_404(Contacto, id_contacto=contacto_id)
    nombre = contacto.nombre_completo

    if request.method == 'POST':
        # Eliminamos el contacto de la base de datos
        # Nota: Si tienes archivos/imágenes, Django no los borra del disco por defecto, 
        # pero el registro desaparecerá.
        contacto.delete()
        
        messages.warning(request, f"El registro de '{nombre}' ha sido eliminado definitivamente del sistema.")
        return redirect('papelera_contactos')

    return redirect('papelera_contactos')







# sector sociales
def sector_sociales(request):
    # Solo traemos los contactos marcados como 'SOCIAL'
    contactos_area_social = Contacto.objects.filter(area='SOCIAL', puesto='Director de Acción Social',activo=True)
    return render(request, "sociales/sector_sociales.html", {'contactos': contactos_area_social})

# 1. Asesoría ANSES
def area_anses(request):
    contactos = Contacto.objects.filter(area='SOCIAL', puesto='Responsable de ANSES', activo=True)
    return render(request, "sociales/area_anses.html", {'contactos': contactos})

# 2. Asuntos Legales
def asuntos_legales(request):
    contactos = Contacto.objects.filter(area='SOCIAL', puesto='Asesor Legal', activo=True)
    return render(request, "sociales/asuntos_legales.html", {'contactos': contactos})

# 3. Niñez y Familia
def ninez_familia(request):
    contactos = Contacto.objects.filter(area='SOCIAL', puesto='Coordinador de Niñez y Familia', activo=True)
    return render(request, "sociales/ninez_familia.html", {'contactos': contactos})

# 4. Adultos Mayores
def adultos_mayores(request):
    contactos = Contacto.objects.filter(area='SOCIAL', puesto='Encargado de Adultos Mayores', activo=True)
    return render(request, "sociales/adultos_mayores.html", {'contactos': contactos})

# 5. Seguridad Ciudadana
def seguridad_ciudadana(request):
    contactos = Contacto.objects.filter(area='SOCIAL', puesto='Director de Seguridad Ciudadana', activo=True)
    return render(request, "sociales/seguridad_ciudadana.html", {'contactos': contactos})



# Habilitaciones Comerciales
def bienvenida_habilitaciones(request):
    return render(request, 'habilitaciones/bienvenida_habilitaciones.html')

@login_required
def solicitar_habilitacion_comercial(request):
    if request.method == 'POST':
        form = SolicitudHabilitacionForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.fecha_solicitud = timezone.now()
            solicitud.save()
            messages.success(
                request,
                "Tu solicitud de habilitación fue enviada y será evaluada por el área correspondiente."
            )
            return redirect('bienvenida')
    else:
        form = SolicitudHabilitacionForm()
    return render(
        request,
        'habilitaciones/solicitud_habilitacion.html',
        {'form': form}
    )

@login_required
@user_passes_test(es_personal) # Admin y Operador gestionan habilitaciones
def gestionar_solicitud_habilitacion(request, id_solicitud, accion):
    solicitud = get_object_or_404(
        SolicitudHabilitacionComercial,
        id_solicitud=id_solicitud
    )

    if solicitud.estado != 'pendiente':
        messages.warning(request, "Esta solicitud ya fue procesada.")
        return redirect('listar_solicitudes_habilitacion')

    if accion == 'aprobar':
        solicitud.estado = 'aprobada'
        solicitud.observacion_admin = request.POST.get(
            'observacion_admin',
            'Solicitud aprobada'
        )
        messages.success(request, "Solicitud aprobada correctamente.")
    elif accion == 'rechazar':
        solicitud.estado = 'rechazada'
        solicitud.observacion_admin = request.POST.get(
            'observacion_admin',
            'Solicitud rechazada'
        )
        messages.error(request, "Solicitud rechazada.")

    solicitud.save()
    return redirect('listar_solicitudes_habilitacion')

@login_required
@user_passes_test(es_personal) # Admin y Operador listan solicitudes
def listar_solicitudes_habilitacion(request):
    query = request.GET.get('q')
    solicitudes = SolicitudHabilitacionComercial.objects.all()

    if query:
        solicitudes = solicitudes.filter(
            Q(nombre_completo__icontains=query) |
            Q(dni__icontains=query) |
            Q(cuit__icontains=query) |
            Q(estado__icontains=query)
        )

    paginator = Paginator(solicitudes.order_by('-fecha_solicitud'), 10)
    page_number = request.GET.get('page')
    solicitudes = paginator.get_page(page_number)

    return render(
        request,
        'habilitaciones/listar_solicitudes.html',
        {'solicitudes': solicitudes}
    )

@login_required
@user_passes_test(es_personal) # Admin y Operador ven detalle
def ver_solicitud_habilitacion(request, id_solicitud):
    solicitud = get_object_or_404(
        SolicitudHabilitacionComercial,
        id_solicitud=id_solicitud
    )
    return render(
        request,
        'habilitaciones/ver_solicitud.html',
        {'solicitud': solicitud}
    )

@login_required
def crear_solicitud_habilitacion(request):
    if request.method == 'POST':
        form = SolicitudHabilitacionForm(
            request.POST,
            request.FILES  # 🔥 CLAVE PARA QUE SE GUARDEN LAS FOTOS
        )
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "La solicitud fue enviada correctamente."
            )
            return redirect('bienvenida_habilitaciones')
    else:
        form = SolicitudHabilitacionForm()
    return render(
        request,
        'habilitaciones/crear_solicitud_habilitacion.html',
        {'form': form}
    )