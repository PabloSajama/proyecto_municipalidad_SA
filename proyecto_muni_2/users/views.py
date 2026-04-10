import secrets
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.core.exceptions import PermissionDenied
from django.db.models import Q, ProtectedError
from django.core.paginator import Paginator
from django.db import transaction, IntegrityError
from functools import wraps
# Modelos
from .models import Perfil, OperadorMunicipal, Area, Puesto, RolMunicipal
from .decorators import solo_super_autorizados, tiene_permiso
from core.models import HistorialVersiones
# Modelos de la app portal
from portal.models import Contacto, ConfiguracionSector, AccesoDirecto, ComponenteSector
from portal.forms import ContactoForm, ConfiguracionSectorForm, AccesoDirectoForm, ComponenteSectorForm
from .forms import RegistroCompletoForm

# --- 1. SEGURIDAD ---

def solo_super_autorizados(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # 1. Verificar autenticación básica
        if not request.user.is_authenticated:
            return redirect('login')
        
        # 2. Verificar si el operador está activo (evita acceso de usuarios "borrados")
        op = getattr(request.user, 'operador', None)
        if op and not op.operador_activo:
            logout(request)
            messages.error(request, "Su cuenta de operador ha sido desactivada.")
            return redirect('login')

        # 3. Verificación de permisos de Superusuario
        # Eliminamos la restricción de que el nombre deba contener "super" o "superior"
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Si no es superusuario, denegar acceso
        raise PermissionDenied 
    return _wrapped_view

# --- 2. MOTOR DE GESTIÓN (POST HANDLER) ---

def _handle_gestion_operador(request):
    accion = request.POST.get('accion')
    
    try:
        with transaction.atomic():
            # --- GESTIÓN DE ÁREAS ---
            if accion == 'crear_area':
                nombre = request.POST.get('nombre_area', '').strip()
                if nombre:
                    Area.objects.create(nombre=nombre.upper())
                    messages.success(request, f"Área '{nombre}' creada correctamente.")

            elif accion == 'editar_area':
                area_id = request.POST.get('area_id')
                nuevo_nombre = request.POST.get('nombre_area', '').strip()
                if nuevo_nombre:
                    area_obj = get_object_or_404(Area, id_area=area_id)
                    area_obj.nombre = nuevo_nombre.upper()
                    area_obj.save()
                    messages.success(request, "Área actualizada correctamente.")

            elif accion == 'eliminar_area':
                area_id = request.POST.get('area_id')
                area_obj = get_object_or_404(Area, id_area=area_id)
                nombre_temp = area_obj.nombre
                area_obj.delete()
                messages.warning(request, f"Área '{nombre_temp}' eliminada.")

            # --- GESTIÓN DE PUESTOS ---
            elif accion == 'crear_puesto':
                nombre_p = request.POST.get('nombre_puesto', '').strip()
                a_id = request.POST.get('area_id')
                if nombre_p and a_id:
                    area_obj = get_object_or_404(Area, id_area=a_id)
                    Puesto.objects.create(nombre=nombre_p.upper(), area=area_obj)
                    messages.success(request, f"Puesto '{nombre_p}' creado.")

            elif accion == 'editar_puesto':
                p_id = request.POST.get('puesto_id')
                nuevo_nombre = request.POST.get('nombre_puesto', '').strip()
                if nuevo_nombre:
                    puesto_obj = get_object_or_404(Puesto, id_puesto=p_id)
                    puesto_obj.nombre = nuevo_nombre.upper()
                    puesto_obj.save()
                    messages.success(request, "Puesto actualizado.")

            # --- GESTIÓN DE OPERADORES ---
            elif accion == 'crear_operador':
                u_name = request.POST.get('username_new', '').strip()
                u_email = request.POST.get('email_new', '').strip()
                p_id = request.POST.get('puesto_id')

                if User.objects.filter(username=u_name).exists():
                    messages.error(request, "El nombre de usuario ya está en uso.")
                    return # El rollback lo hace el contexto de la transacción

                puesto_obj = get_object_or_404(Puesto, id_puesto=p_id)
                
                # Generación de contraseña segura
                alfabeto = string.ascii_letters + string.digits + "!@#$%"
                pwd = ''.join(secrets.choice(alfabeto) for _ in range(12))
                
                nuevo_user = User.objects.create_user(username=u_name, email=u_email, password=pwd)
                nuevo_user.is_staff = True
                nuevo_user.save()

                # Lógica de Legajo mejorada
                ultimo_op = OperadorMunicipal.objects.all().order_by('id').last()
                proximo_num = 1
                if ultimo_op and ultimo_op.legajo and '-' in ultimo_op.legajo:
                    try:
                        proximo_num = int(ultimo_op.legajo.split('-')[1]) + 1
                    except (ValueError, IndexError):
                        proximo_num = OperadorMunicipal.objects.count() + 1
                
                nuevo_legajo = f"MUN-{proximo_num:04d}"

                OperadorMunicipal.objects.create(
                    user=nuevo_user, 
                    area=puesto_obj.area, 
                    puesto=puesto_obj,
                    legajo=nuevo_legajo, 
                    requiere_cambio_password=True,
                    operador_activo=True
                )
                messages.success(request, f"ALTA EXITOSA. Legajo: {nuevo_legajo} | CLAVE: {pwd}")

            elif accion == 'modificar_rol':
                user_id = request.POST.get('user_id')
                rol_slug = request.POST.get('rol_asignado') 
                target_user = get_object_or_404(User, id=user_id)
                operador = target_user.operador
                
                if rol_slug == 'superadmin':
                    operador.rol = RolMunicipal.SUPER_USUARIO
                    target_user.is_superuser = target_user.is_staff = True
                elif rol_slug == 'admin':
                    operador.rol = RolMunicipal.ADMINISTRADOR
                    target_user.is_superuser = False
                    target_user.is_staff = True
                else:
                    operador.rol = RolMunicipal.OPERADOR
                    target_user.is_superuser = target_user.is_staff = False
                
                operador.save()
                target_user.save()

                if request.user.id == target_user.id:
                    update_session_auth_hash(request, target_user)
                messages.success(request, f"Permisos de @{target_user.username} actualizados.")

            elif accion == 'eliminar_operador':
                op_id = request.POST.get('op_id')
                operador = get_object_or_404(OperadorMunicipal, id=op_id)
                
                # Soft delete (Desactivación)
                operador.operador_activo = False
                operador.save()
                operador.user.is_active = False
                operador.user.save()
                messages.warning(request, f"Agente @{operador.user.username} desactivado.")

    except ProtectedError:
        messages.error(request, "No se puede eliminar: existen registros relacionados (historial, trámites, etc.).")
    except IntegrityError as e:
        messages.error(request, f"Error de base de datos: {str(e)}")
    except Exception as e:
        messages.error(request, f"Error inesperado: {str(e)}")


@login_required
@solo_super_autorizados
def admin_superior_panel(request):
    if request.method == 'POST':
        _handle_gestion_operador(request)
        return redirect('admin_superior_panel')

    q_op = request.GET.get('q_op', '')
    
    # Filtramos solo por operadores activos para la lista de gestión
    operadores_list = OperadorMunicipal.objects.select_related('user', 'area', 'puesto').filter(operador_activo=True)
    
    if q_op:
        operadores_list = operadores_list.filter(Q(user__username__icontains=q_op) | Q(legajo__icontains=q_op))

    pag_op = Paginator(operadores_list, 10)
    operadores = pag_op.get_page(request.GET.get('page_op'))
    
    try:
        logs = HistorialVersiones.objects.select_related('usuario').all().order_by('-fecha')[:10]
    except:
        logs = []

    context = {
        'operadores': operadores,
        'areas': Area.objects.all().prefetch_related('puestos'),
        'q_op': q_op,
        'logs': logs,
    }
    return render(request, 'users/admin_superior.html', context)

@login_required
@solo_super_autorizados
def ver_usuario_operador(request, user_id):
    usuario_target = get_object_or_404(User, id=user_id)
    operador = getattr(usuario_target, 'operador', None)
    
    # Permitimos ver el perfil incluso si está inactivo (para auditoría), 
    # pero avisamos visualmente en el template.
    if not operador:
        messages.error(request, "El usuario seleccionado no posee un perfil laboral.")
        return redirect('admin_superior_panel')

    historial_list = HistorialVersiones.objects.filter(usuario=usuario_target).order_by('-fecha')
    paginator = Paginator(historial_list, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'users/ver_usuario_operador.html', {
        'u': usuario_target,
        'operador': operador,
        'historial': page_obj,
    })

# --- 4. AUTENTICACIÓN Y REGISTRO ---

def login_view(request):
    if request.user.is_authenticated:
        return redirect('bienvenida')
    
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        
        if user:
            # Validación de Operador Activo
            op = getattr(user, 'operador', None)
            if op and not op.operador_activo:
                messages.error(request, "Su cuenta de personal ha sido desactivada. Contacte a soporte.")
                return render(request, 'users/login.html')

            if not user.is_active:
                messages.error(request, "Su usuario de sistema se encuentra inactivo.")
                return render(request, 'users/login.html')

            login(request, user)
            if op and op.requiere_cambio_password:
                messages.warning(request, "Acceso inicial detectado. Debe cambiar su contraseña.")
                return redirect('cambiar_password_operador')
            return redirect('bienvenida')
        
        messages.error(request, "Usuario o contraseña incorrectos.")
    return render(request, 'users/login.html')

def registro_view(request):
    if request.user.is_authenticated:
        return redirect('bienvenida')

    if request.method == 'POST':
        form = RegistroCompletoForm(request.POST)
        if form.is_valid():
            form.save() # Esto guarda User y Perfil automáticamente
            messages.success(request, "Registro completo. Ya puede iniciar sesión.")
            return redirect('login')
    else:
        form = RegistroCompletoForm()
    
    return render(request, 'users/registro.html', {'form': form})


@login_required
def cambiar_password_operador(request):
    operador = getattr(request.user, 'operador', None)
    if not operador or not operador.operador_activo:
        messages.error(request, "Acceso restringido o perfil inactivo.")
        logout(request)
        return redirect('login')

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            operador.requiere_cambio_password = False
            operador.save()
            messages.success(request, "Contraseña laboral actualizada correctamente.")
            return redirect('bienvenida')
    else:
        form = PasswordChangeForm(request.user)
        
    return render(request, 'users/cambiar_password_operador.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('login')

# --- 5. GESTIÓN DE PANTALLAS (PORTAL) ---

@login_required
def lista_pantallas(request):
    operador = getattr(request.user, 'operador', None)
    if not operador or not operador.operador_activo:
        messages.error(request, "Requiere perfil de operador activo.")
        logout(request)
        return redirect('login')

    # Ordenamos por ID de forma ascendente
    pantallas = ConfiguracionSector.objects.filter(area=operador.area).order_by('id')
    
    return render(request, 'users/lista_pantallas.html', {
        'pantallas': pantallas,
        'operador': operador
    })

@login_required
def editar_pantalla(request, pk):
    # 1. Obtención del perfil del operador y validación de seguridad
    operador = getattr(request.user, 'operador', None)
    
    if not operador or not operador.operador_activo:
        messages.error(request, "Acceso denegado: Su perfil de operador no está activo o no existe.")
        logout(request)
        return redirect('bienvenida')

    # --- BLOQUE DE SEGURIDAD RESTAURADO ---
    config_web = get_object_or_404(ConfiguracionSector, pk=pk)
    # Si el área de la pantalla NO es la misma que la del operador, no entra
    if operador.area != config_web.area:
        messages.error(request, "No tienes permiso para editar pantallas de otro sector.")
        # Aquí usa el nombre de la URL de tu lista de pantallas (sin el 'users:')
        return redirect('lista_pantallas') 
    # --------------------------------------

    # 2. Obtener la instancia asegurando que pertenece al área del operador
    config_web = get_object_or_404(ConfiguracionSector, pk=pk, area=operador.area)
    
    # 3. Obtener la instancia de contacto para el área
    contacto_instancia = Contacto.objects.filter(area=operador.area).first()

    # 4. Definición de los Formsets
    AccesoFormSet = inlineformset_factory(
        ConfiguracionSector, 
        AccesoDirecto, 
        form=AccesoDirectoForm,
        extra=0, 
        can_delete=True
    )

    ComponenteFormSet = inlineformset_factory(
        ConfiguracionSector,
        ComponenteSector,
        form=ComponenteSectorForm,
        extra=0,
        can_delete=True
    )

    # 5. Procesamiento del envío del formulario (POST)
    if request.method == 'POST':
        form_config = ConfiguracionSectorForm(request.POST, request.FILES, instance=config_web)
        
        # CORRECCIÓN: Pasamos el usuario (user=request.user) al formulario de contacto
        form_contacto = ContactoForm(request.POST, instance=contacto_instancia, user=request.user)
        
        formset_accesos = AccesoFormSet(
            request.POST, 
            request.FILES, 
            instance=config_web, 
            prefix='accesos'
        )
        formset_componentes = ComponenteFormSet(
            request.POST, 
            request.FILES, 
            instance=config_web, 
            prefix='componentes'
        )

        if all([
            form_config.is_valid(), 
            form_contacto.is_valid(), 
            formset_accesos.is_valid(), 
            formset_componentes.is_valid()
        ]):
            conf = form_config.save(commit=False)
            
            # Seguridad: Solo superusuarios cambian la URL de destino final
            if not request.user.is_superuser:
                conf.url_destino = config_web.url_destino
            
            conf.save()
            form_contacto.save()
            formset_accesos.save()
            formset_componentes.save()
            
            messages.success(request, f"¡Los cambios en '{config_web.nombre_pantalla}' se guardaron con éxito!")
            return redirect('lista_pantallas')
        else:
            messages.error(request, "Por favor, corrija los errores marcados en el formulario.")
    
    # 6. Carga inicial de formularios (GET)
    else:
        form_config = ConfiguracionSectorForm(instance=config_web)
        
        # CORRECCIÓN: También pasamos el usuario en el método GET
        form_contacto = ContactoForm(instance=contacto_instancia, user=request.user)
        
        formset_accesos = AccesoFormSet(instance=config_web, prefix='accesos')
        formset_componentes = ComponenteFormSet(instance=config_web, prefix='componentes')

    # 7. Renderizado
    return render(request, 'users/editar_pantalla_sector.html', {
        'form_config': form_config, 
        'form_contacto': form_contacto,
        'formset_accesos': formset_accesos,
        'formset_componentes': formset_componentes,
        'pantalla': config_web,
        'operador': operador
    })