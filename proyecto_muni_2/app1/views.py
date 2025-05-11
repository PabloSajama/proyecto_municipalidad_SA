from django.shortcuts import render , redirect , get_list_or_404 , get_object_or_404 # type: ignore


def bienvenida(request):
    return render(request, 'bienvenida.html')

def login(request):
    return render(request, 'login.html')

def registro(request):
    return render(request, 'registro.html')

def entrada(request):
    return render(request, 'entrada.html')

def contactos(request):
    return render(request, 'contactos.html')

def servicios(request):
    return render(request, 'servicios.html')