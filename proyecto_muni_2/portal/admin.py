from django.contrib import admin
from .models import Noticia, Eventos, Contacto, ConfiguracionSector, AccesoDirecto, ComponenteSector

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'area', 'autor', 'fecha_creacion', 'activo')
    list_filter = ('area', 'activo')

@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'area', 'puesto', 'activo')
    list_filter = ('area',)

@admin.register(Eventos)
class EventosAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'lugar', 'fecha', 'user', 'activo')
    list_filter = ('activo', 'fecha')

@admin.register(ConfiguracionSector)
class ConfiguracionSectorAdmin(admin.ModelAdmin):
    list_display = ('area', 'titulo_portal', 'subtitulo_portal')
    list_filter = ('area',)
    prepopulated_fields = {"slug_pantalla": ("nombre_pantalla",)}

@admin.register(AccesoDirecto)
class AccesoDirectoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'url_destino', 'activo')
    list_filter = ('activo',)

@admin.register(ComponenteSector)
class ComponenteSectorAdmin(admin.ModelAdmin):
    # Añadimos 'configuracion' para saber a qué pantalla pertenece cada bloque
    list_display = ('titulo', 'tipo', 'orden', 'configuracion', 'activo')
    # Filtramos por configuración para buscar más rápido
    list_filter = ('configuracion', 'tipo', 'activo')
    # Permitimos editar el orden y el activo desde la lista directamente
    list_editable = ('orden', 'activo') 
    search_fields = ('titulo', 'contenido')