from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.contrib import messages
from .forms import RegistroForm, LoginForm, NoticiaForm, CatastroForm, EventoForm, ContactoForm
from .models import Noticia , Catastros, Eventos, ConsultasSociales, Contacto
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required

#vista inicio
def bienvenida(request):
    noticias = Noticia.objects.filter(activo=True).order_by('-fecha_publicacion')[:6]
    return render(request, 'bienvenida.html', {'noticias': noticias})



def lista_servicios(request):
    return render(request, 'lista_servicios.html')

def informacion(request):
    return render(request, 'informacion.html')






# Vistas para noticias

def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def crear_noticia(request):
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES)
        if form.is_valid():
            noticia = form.save(commit=False)
            noticia.user = request.user
            noticia.save()
            return redirect('lista_noticias')  # cambia por el nombre real de la url
    else:
        form = NoticiaForm()
    return render(request, 'crear_noticia.html', {'form': form})

# Vista para listar noticias
def lista_noticias(request):
    noticias = Noticia.objects.filter(activo=True).order_by('fecha_publicacion')
    return render(request, 'lista_noticias.html', {'noticias': noticias, 'user': request.user})


# vista para eliminar noticias 
@login_required
@user_passes_test(is_admin)
def eliminar_noticia(request, id_noticia):
    if request.method == 'POST':
        noticia = get_object_or_404(Noticia, pk=id_noticia)
        # Soft delete: aquí podés usar un campo booleano como 'activo' para ocultar
        noticia.activo = False
        noticia.save()
        return redirect('lista_noticias')
    else:
        return HttpResponseForbidden()  # Si intentan acceder con GET, denegar

# Vista para ver detalle de una noticia
def ver_noticia(request, id_noticia):
    noticia = get_object_or_404(Noticia, id_noticia=id_noticia, activo=True)
    return render(request, 'ver_noticia.html', {'noticia': noticia})

# Vista para editar una noticia
@login_required
@user_passes_test(is_admin)
@login_required
@user_passes_test(is_admin)
def editar_noticia(request, id_noticia):
    noticia = get_object_or_404(Noticia, pk=id_noticia)
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES, instance=noticia)
        if form.is_valid():
            # Si el usuario marcó el checkbox nativo de Django para limpiar la imagen:
            if request.POST.get('imagen_principal-clear') == 'on':
                if noticia.imagen_principal:
                    noticia.imagen_principal.delete(save=False)
                noticia.imagen_principal = None

            # Guardar cambios (si se subió una nueva imagen, form.save la aplicará)
            form.save()
            messages.success(request, 'Noticia actualizada correctamente.')
            return redirect('lista_noticias')
    else:
        form = NoticiaForm(instance=noticia)

    return render(request, 'editar_noticia.html', {'form': form, 'noticia': noticia})









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
    return render(request, 'registro.html', {'form': form})

# Vista para login
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            return redirect('bienvenida')  # Cambia esto a tu url principal
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# Vista para logout
def logout_view(request):
    logout(request)
    return redirect('login')






# Vistas para Catastro


def catastro_info(request):
    return render(request, 'catastro.html')



# Vista para crear catastro (solo admin)
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def crear_catastro(request):
    if request.method == 'POST':
        form = CatastroForm(request.POST, request.FILES)  # Asegurate de incluir request.FILES si usás imagen
        if form.is_valid():
            catastro = form.save(commit=False)
            catastro.eliminado = False  # Asegura que se cree como "no eliminado"
            catastro.save()
            return redirect('listar_catastros')
    else:
        form = CatastroForm()

    return render(request, 'crear_catastro.html', {'form': form})

# Vista para listar catastros (solo admin)
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def listar_catastros(request):
    queryset = Catastros.objects.filter(eliminado=False)
    dni = request.GET.get('dni')
    numero = request.GET.get('numero')
    nombre = request.GET.get('nombre')

    # Filtros
    if dni:
        queryset = queryset.filter(dni_propietario__icontains=dni)
    if numero:
        queryset = queryset.filter(numero_catastro__icontains=numero)
    if nombre:
        # Este filtro solo aplica si tenés un campo nombre_propietario en el modelo
        queryset = queryset.filter(nombre_propietario__icontains=nombre)

    return render(request, 'listar_catastros.html', {
        'catastros': queryset,
        'dni': dni,
        'numero': numero,
        'nombre': nombre,
    })



# Vista para eliminar catastro (soft delete, solo admin)
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def eliminar_catastro(request, id_catastro):
    if request.method == 'POST':
        catastro = get_object_or_404(Catastros, id_catastro=id_catastro, eliminado=False)
        catastro.eliminado = True
        catastro.save()
        return redirect('listar_catastros')
    else:
        return HttpResponseForbidden("Acción no permitida.")


# vista para ver detalle de un catastro

@login_required(login_url='login')
def ver_catastro(request, id_catastro):
    catastro = get_object_or_404(Catastros, id_catastro=id_catastro, eliminado=False)
    return render(request, 'ver_catastro.html', {'catastro': catastro})


# vista para editar un catastro (solo admin)
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def editar_catastro(request, id_catastro):
    catastro = get_object_or_404(Catastros, id_catastro=id_catastro)

    if request.method == 'POST':
        form = CatastroForm(request.POST, request.FILES, instance=catastro)
        if form.is_valid():
            form.save()
            return redirect('listar_catastros')
    else:
        form = CatastroForm(instance=catastro)

    return render(request, 'editar_catastro.html', {
        'form': form,
        'catastro': catastro
    })



# Eventos

# ---------- VISTA DEL CALENDARIO ----------
def eventos(request):
    eventos = Eventos.objects.filter(activo=True)
    return render(request, "eventos.html", {"eventos": eventos})

# ---------- CREAR EVENTO (solo admin) ----------
@user_passes_test(lambda u: u.is_staff)
def crear_evento(request):
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.user = request.user
            evento.fecha_publicacion = timezone.now().date()  # Asignar la fecha actual
            evento.save()
            return redirect('eventos')
    else:
        form = EventoForm()
    return render(request, 'crear_evento.html', {'form': form})


# ---------- EDITAR EVENTO (solo admin) ----------
@user_passes_test(lambda u: u.is_staff)
def editar_evento(request, evento_id):
    evento = get_object_or_404(Eventos, pk=evento_id)
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            return redirect('eventos')
    else:
        form = EventoForm(instance=evento)
    return render(request, 'editar_evento.html', {'form': form, 'evento': evento})


# ---------- ELIMINAR EVENTO (solo admin) ----------
@user_passes_test(lambda u: u.is_staff)
def eliminar_evento(request, evento_id):
    evento = get_object_or_404(Eventos, pk=evento_id)
    evento.activo = False
    evento.save()
    return redirect('eventos')



# Rentas

def renta_info(request):
    return render(request, 'rentas.html')

def tasas_municipales(request):
    return render(request, "tasas.html")

def regularizaciones(request):
    return render(request, "regularizaciones.html")



# quienes somos


def autoridades_view(request):
    return render(request, "autoridades.html")

def historia(request):
    return render(request, 'historia.html')

def intendencias(request):
    return render(request, "intendencias.html")

def organigrama(request):
    return render(request, "organigrama.html")





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
        # Podés redirigir a una página de éxito o volver al mismo formulario
        return redirect('consultas')  # suponiendo que la URL para el formulario es 'consultas'
    else:
        return render(request, "consultas.html")
    

@staff_member_required
def ver_consultas(request):
    consultas = ConsultasSociales.objects.all().order_by('-fecha_envio')
    return render(request, "ver_consultas.html", {"consultas": consultas})

@staff_member_required
def eliminar_consulta(request, id_consulta):
    if request.method == 'POST':
        consulta = get_object_or_404(ConsultasSociales, id_consulta=id_consulta)
        consulta.delete()
        return redirect('ver_consultas')
    else:
        return HttpResponseForbidden("Acción no permitida.")
    
@staff_member_required
def ver_consulta_individual(request, id_consulta):
    consulta = get_object_or_404(ConsultasSociales, pk=id_consulta)
    return render(request, "ver_consulta_individual.html", {"consulta": consulta})





# ver contactos



def contactos(request):
    contactos = Contacto.objects.all()
    return render(request, 'contactos.html', {'contactos': contactos})

def ver_contacto(request, contacto_id):
    contacto = get_object_or_404(Contacto, pk=contacto_id)
    return render(request, "ver_contacto.html", {"contacto": contacto})


@staff_member_required
def crear_contacto(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Contacto creado correctamente.")
            return redirect('contactos')  # Cambia esto a la URL que uses para listar contactos
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = ContactoForm()

    return render(request, 'crear_contacto.html', {'form': form})

@staff_member_required
def eliminar_contacto(request, contacto_id):
    contacto = get_object_or_404(Contacto, pk=contacto_id)
    contacto.delete()
    messages.success(request, "Contacto eliminado correctamente.")
    return redirect('contactos')  # nombre de la URL para ver todos los contactos