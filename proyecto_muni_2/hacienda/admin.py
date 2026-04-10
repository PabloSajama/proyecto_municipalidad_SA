from django.contrib import admin
from .models import Rentas, ArchivosRenta, SolicitudHabilitacionComercial

@admin.register(Rentas)
class RentasAdmin(admin.ModelAdmin):
    list_display = ('perfil', 'tipo_tasa', 'monto_deuda', 'pagado')
    list_filter = ('pagado', 'tipo_tasa')

@admin.register(SolicitudHabilitacionComercial)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ('nombre_comercio', 'cuit', 'estado', 'fecha_creacion')
    list_filter = ('estado',)
    search_fields = ('nombre_comercio', 'cuit')