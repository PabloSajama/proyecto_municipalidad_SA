from django.contrib import admin
from .models import Noticia, Eventos, Contacto, ConfiguracionSector, AccesoDirecto, ComponenteSector, NotaRecordatorio, ArchivadorImagen

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    # Agregamos subarea a la lista y al filtro
    list_display = ('titulo', 'area', 'subarea', 'autor', 'fecha_creacion', 'activo')
    list_filter = ('area', 'subarea', 'activo')
    search_fields = ('titulo', 'texto')
    prepopulated_fields = {'slug': ('titulo',)}

@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    # La subárea ayuda a identificar oficinas específicas en la lista de contactos
    list_display = ('nombre_completo', 'area', 'subarea', 'puesto', 'activo')
    list_filter = ('area', 'subarea', 'activo')
    search_fields = ('nombre_completo', 'telefono', 'correo')

@admin.register(Eventos)
class EventosAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'lugar', 'fecha', 'user', 'activo')
    list_filter = ('activo', 'fecha')

@admin.register(ConfiguracionSector)
class ConfiguracionSectorAdmin(admin.ModelAdmin):
    # Agregamos subarea para saber si es una configuración de oficina o de área general
    list_display = ('area', 'subarea', 'titulo_portal', 'subtitulo_portal')
    list_filter = ('area', 'subarea')
    prepopulated_fields = {"slug_pantalla": ("nombre_pantalla",)}

@admin.register(AccesoDirecto)
class AccesoDirectoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'url_destino', 'activo')
    list_filter = ('activo',)

@admin.register(ComponenteSector)
class ComponenteSectorAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'orden', 'configuracion', 'activo')
    list_filter = ('configuracion', 'tipo', 'activo')
    list_editable = ('orden', 'activo') 
    search_fields = ('titulo', 'contenido')

# --- Gestión de Notas y Recordatorios ---

class ImagenNotaInline(admin.TabularInline):
    model = ArchivadorImagen
    extra = 1  
    fields = ['imagen']

@admin.register(NotaRecordatorio)
class NotaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_actual', 'fecha_designada', 'completada', 'usuario')
    list_filter = ('completada', 'fecha_actual', 'usuario')
    search_fields = ('titulo', 'contenido')
    inlines = [ImagenNotaInline]
    fieldsets = (
        ('Información Principal', {
            'fields': ('usuario', 'titulo', 'contenido')
        }),
        ('Planificación', {
            'fields': ('fecha_designada', 'completada', 'activo'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ArchivadorImagen)
class ImagenNotaAdmin(admin.ModelAdmin):
    list_display = ('nota', 'imagen')