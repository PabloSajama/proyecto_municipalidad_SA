from django.contrib import admin
from .models import Noticia, Eventos, Contacto, ConfiguracionSector, AccesoDirecto, ComponenteSector, NotaRecordatorio, ArchivadorImagen

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


# Configuración para que las imágenes aparezcan dentro de la Nota
# Configuración para que las imágenes aparezcan dentro de la Nota
class ImagenNotaInline(admin.TabularInline):
    model = ArchivadorImagen
    extra = 1  
    fields = ['imagen']

@admin.register(NotaRecordatorio)
class NotaAdmin(admin.ModelAdmin):
    # Cambié 'user' por 'usuario' (verificá si este es el nombre en tu modelo)
    list_display = ('titulo', 'fecha_actual', 'fecha_designada', 'completada', 'usuario')
    
    # Cambié 'user' por 'usuario'
    list_filter = ('completada', 'fecha_actual', 'usuario')
    
    search_fields = ('titulo', 'contenido')
    
    inlines = [ImagenNotaInline]

    fieldsets = (
        ('Información Principal', {
            # Cambié 'user' por 'usuario'
            'fields': ('usuario', 'titulo', 'contenido')
        }),
        ('Planificación', {
            'fields': ('fecha_designada', 'completada'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ArchivadorImagen)
class ImagenNotaAdmin(admin.ModelAdmin):
    list_display = ('nota', 'imagen')