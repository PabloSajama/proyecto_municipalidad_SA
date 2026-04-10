from django.contrib import admin
from .models import Area, Puesto, Perfil, OperadorMunicipal

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('id_area', 'nombre')

@admin.register(Puesto)
class PuestoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'area')
    list_filter = ('area',)

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('dni', 'nombre_completo', 'user')
    search_fields = ('dni', 'nombre_completo')

@admin.register(OperadorMunicipal)
class OperadorAdmin(admin.ModelAdmin):
    list_display = ('user', 'legajo', 'area', 'puesto', 'activo')
    list_filter = ('area', 'activo')
    search_fields = ('legajo', 'user__username')