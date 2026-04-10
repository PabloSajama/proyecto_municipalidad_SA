# En portal/utils.py o core/utils.py

from portal.models import ConfiguracionSector, Contacto
from django.apps import apps

def get_pantalla_data(area_name, slug):
    """
    Recupera la configuración y sus relaciones dinámicamente.
    """
    # Usamos apps.get_model para evitar importaciones circulares si este archivo
    # es llamado desde modelos o vistas de distintas apps.
    ConfiguracionSector = apps.get_model('portal', 'ConfiguracionSector')
    Contacto = apps.get_model('portal', 'Contacto')
    
    # Buscamos la configuración con select_related para traer el área de una sola vez
    config = ConfiguracionSector.objects.filter(
        area__nombre__icontains=area_name, 
        slug_pantalla=slug
    ).select_related('area').first()
    
    if not config:
        return None

    # --- Lógica de Componentes ---
    # Es mejor definir un related_name fijo en el modelo, pero si varían:
    componentes = []
    # Priorizamos el nombre más común en Django (modelname_set)
    for attr in ['componentesector_set', 'componentes', 'componente_set']:
        related_manager = getattr(config, attr, None)
        if related_manager:
            # Verificamos que tenga el método filter (para confirmar que es un Manager)
            componentes = related_manager.filter(activo=True).order_by('orden')
            break

    # --- Lógica de Accesos ---
    accesos = []
    for attr in ['accesodirecto_set', 'accesos', 'acceso_set']:
        related_manager = getattr(config, attr, None)
        if related_manager:
            accesos = related_manager.filter(activo=True).order_by('orden')
            break

    return {
        "config": config,
        "contacto": Contacto.objects.filter(area=config.area, activo=True).first(),
        "accesos": accesos,
        "componentes": componentes
    }