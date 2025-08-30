from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.contrib import messages
from .forms import RegistroForm, LoginForm, NoticiaForm, CatastroForm
from .models import Noticia , Catastros

def bienvenida(request):
    noticias = Noticia.objects.filter(activo=True).order_by('-fecha_publicacion')[:6]  # últimas 6 noticias activas
    return render(request, 'bienvenida.html', {'noticias': noticias})


def contactos(request):
    return render(request, 'contactos.html')

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
    
def ver_noticia(request, noticia_id):
    noticia = get_object_or_404(Noticia, id_noticia=noticia_id, activo=True)
    return render(request, 'ver_noticia.html', {'noticia': noticia})








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

def logout_view(request):
    logout(request)
    return redirect('login')






# Vistas para Catastro

def catastro_info(request):
    return render(request, 'catastro.html')


@login_required(login_url='login')
def buscar_catastro(request):
    numero = request.GET.get('numero_catastro')
    dni = request.GET.get('dni_propietario')

    resultados = Catastros.objects.filter(eliminado=False)

    if numero:
        resultados = resultados.filter(numero_catastro__icontains=numero)

    if dni:
        resultados = resultados.filter(dni_propietario__icontains=dni)

    mensaje = ''
    if not resultados.exists():
        mensaje = "No se encontraron resultados."

    return render(request, 'buscar_catastro.html', {
        'resultados': resultados,
        'mensaje': mensaje,
    })


@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def crear_catastro(request):
    if request.method == 'POST':
        form = CatastroForm(request.POST, request.FILES)  # Asegurate de incluir request.FILES si usás imagen
        if form.is_valid():
            catastro = form.save(commit=False)
            catastro.eliminado = False  # Asegura que se cree como "no eliminado"
            catastro.save()
            return redirect('buscar_catastro')
    else:
        form = CatastroForm()

    return render(request, 'crear_catastro.html', {'form': form})

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