from django.contrib import admin
from .models import HistorialVersiones

@admin.register(HistorialVersiones)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'usuario', 'tabla', 'accion')
    readonly_fields = ('fecha', 'usuario', 'tabla', 'accion', 'datos_anteriores', 'datos_nuevos')