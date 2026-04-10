from django.shortcuts import render, get_object_or_404, Http404
from portal.models import Contacto,ConfiguracionSector, AccesoDirecto, ComponenteSector
from users.utils import get_pantalla_data 

# 1. INICIO (La que ya tenías)
def inicio_rentas(request):
    context = get_pantalla_data(area_name="RENTA", slug="inicio_rentas")
    if not context:
        raise Http404("La configuración para esta pantalla no existe.")
    return render(request, "rentas/inicio_rentas.html", context)

# 2. AUTOMOTOR
def automotor(request):
    context = get_pantalla_data(area_name="RENTA", slug="automotor")
    if not context:
        raise Http404("La configuración para Automotor no existe.")
    return render(request, "rentas/automotor.html", context)

# 3. LICENCIA DE CONDUCIR
def licencia_conducir(request):
    context = get_pantalla_data(area_name="RENTA", slug="licencia_conducir")
    if not context:
        raise Http404("La configuración para Licencia de Conducir no existe.")
    return render(request, "rentas/licencia_conducir.html", context)

# 4. IMPUESTO INMOBILIARIO
def impuesto_inmobiliario(request):
    context = get_pantalla_data(area_name="RENTA", slug="impuesto_inmobiliario")
    if not context:
        raise Http404("La configuración para Impuesto Inmobiliario no existe.")
    return render(request, "rentas/impuesto_inmobiliario.html", context)

# 5. HABILITACIONES DE NEGOCIO
def habilitaciones_negocio(request):
    context = get_pantalla_data(area_name="RENTA", slug="habilitaciones_negocio")
    if not context:
        raise Http404("La configuración para Habilitaciones de Negocio no existe.")
    return render(request, "rentas/habilitaciones_negocio.html", context)

# 6. ALUMBRADO Y LIMPIEZA
def alumbrado_limpieza(request):
    context = get_pantalla_data(area_name="RENTA", slug="alumbrado_limpieza")
    if not context:
        raise Http404("La configuración para Alumbrado y Limpieza no existe.")
    return render(request, "rentas/alumbrado_limpieza.html", context)



## VIstas para Licencia de Conducir, Impuesto Inmobiliario, Habilitaciones de Negocio y Alumbrado y Limpieza

def inicio_licencia(request):
    context = get_pantalla_data(area_name="LICENCIA", slug="inicio_licencia")
    if not context:
        raise Http404("La configuración para esta pantalla no existe.")
    return render(request, "licencias/inicio_licencia.html", context)