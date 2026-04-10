from django.shortcuts import render, get_object_or_404, Http404
from portal.models import Contacto,ConfiguracionSector, AccesoDirecto, ComponenteSector
from users.utils import get_pantalla_data 


def inicio_catastro(request):
    # Usamos la función para traer TODA la info de una vez
    context = get_pantalla_data(area_name="CATASTRO", slug="inicio_catastro")

    # Si no existe la configuración en la DB, lanzamos un 404 o redirigimos
    if not context:
        raise Http404("La configuración para esta pantalla no existe.")

    # Renderizamos el HTML con el diccionario 'context' que ya trae:
    # config, contacto, accesos y componentes.
    return render(request, "catastro/inicio_catastro.html", context)