from django.contrib import admin
from .models import ConsultasSociales, EventosSociales, Reclamo

@admin.register(ConsultasSociales)
class ConsultasSocialesAdmin(admin.ModelAdmin):
    # Agregamos area y subarea destino para saber a dónde va dirigida la consulta
    list_display = ('id_consulta', 'asunto', 'usuario', 'area_destino', 'subarea_destino', 'fecha_envio', 'respondida')
    # Filtros por áreas y estado de respuesta
    list_filter = ('respondida', 'area_destino', 'subarea_destino', 'fecha_envio')
    search_fields = ('asunto', 'usuario__dni', 'usuario__username', 'mensaje')
    readonly_fields = ('fecha_envio',)
    
    # Agrupamos en el formulario de edición
    fieldsets = (
        ('Información de la Consulta', {
            'fields': ('usuario', 'asunto', 'mensaje', 'fecha_envio')
        }),
        ('Destino', {
            'fields': ('area_destino', 'subarea_destino')
        }),
        ('Gestión de Respuesta', {
            'fields': ('respondida', 'respuesta_municipio', 'fecha_respuesta')
        }),
    )

@admin.register(EventosSociales)
class EventosSocialesAdmin(admin.ModelAdmin):
    # Mostramos el área y subárea que organiza el evento
    list_display = ('titulo', 'lugar', 'area', 'subarea', 'fecha_hora', 'activo')
    list_filter = ('activo', 'area', 'subarea', 'fecha_hora', 'lugar')
    search_fields = ('titulo', 'descripcion')

@admin.register(Reclamo)
class ReclamoAdmin(admin.ModelAdmin):
    # Esta es la tabla que faltaba
    list_display = ('id_reclamo', 'asunto', 'usuario', 'area_destino', 'subarea_destino', 'fecha_envio', 'respondido')
    # Filtros para que el admin vea reclamos por oficina específica
    list_filter = ('respondido', 'area_destino', 'subarea_destino', 'fecha_envio')
    search_fields = ('asunto', 'usuario__dni', 'usuario__username', 'mensaje')
    readonly_fields = ('fecha_envio',)

    fieldsets = (
        ('Detalle del Reclamo', {
            'fields': ('usuario', 'asunto', 'mensaje', 'fecha_envio')
        }),
        ('Asignación', {
            'fields': ('area_destino', 'subarea_destino')
        }),
        ('Resolución', {
            'fields': ('respondido', 'respuesta_municipio', 'fecha_respuesta')
        }),
    )