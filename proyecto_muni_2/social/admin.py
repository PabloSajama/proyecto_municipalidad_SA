from django.contrib import admin
from .models import ConsultasSociales, EventosSociales

@admin.register(ConsultasSociales)
class ConsultasSocialesAdmin(admin.ModelAdmin):
    # Mostramos si fue respondida para que el Admin sepa qué tiene pendiente
    list_display = ('asunto', 'usuario', 'fecha_envio', 'respondida')
    list_filter = ('respondida', 'fecha_envio')
    search_fields = ('asunto', 'usuario__dni', 'usuario__user__username')
    # Hacemos que la fecha sea de solo lectura para integridad
    readonly_fields = ('fecha_envio',)

@admin.register(EventosSociales)
class EventosSocialesAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'lugar', 'fecha_hora', 'activo')
    list_filter = ('activo', 'fecha_hora', 'lugar')
    search_fields = ('titulo', 'descripcion')