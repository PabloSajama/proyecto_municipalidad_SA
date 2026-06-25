from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Area, SubArea, Puesto, Perfil, OperadorMunicipal

# --- CONTROL AVANZADO DE USUARIOS (Para ver DNI, Legajo, Nombre y Roles juntos) ---
# Desregistramos el User original para meter nuestra versión mejorada
admin.site.unregister(User)

@admin.register(User)
class PersonalizadoUserAdmin(UserAdmin):
    # Modificamos las columnas de la tabla principal (la de tu captura de pantalla)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_dni', 'get_legajo_y_rol', 'is_staff', 'is_active')
    
    # Filtros laterales para separar rápido en el panel derecho
    list_filter = ('is_staff', 'is_active', 'operador__rol', 'operador__area')
    
    # Buscador para poder tipear DNI o Legajo en la barra de arriba
    search_fields = ('username', 'email', 'first_name', 'last_name', 'perfil__dni', 'operador__legajo')

    # Métodos seguros para extraer los datos de tus modelos relacionados sin que rompa nada
    def get_dni(self, instance):
        perfil = getattr(instance, 'perfil', None)
        return perfil.dni if (perfil and perfil.dni) else '-'
    get_dni.short_description = 'DNI (Invitado)'

    def get_legajo_y_rol(self, instance):
        operador = getattr(instance, 'operador', None)
        if operador:
            return f"{operador.legajo} - {operador.get_rol_display()} ({operador.area.nombre if operador.area else 'Sin Área'})"
        if instance.is_superuser:
            return "Superusuario"
        return "Invitado / Externo"
    get_legajo_y_rol.short_description = 'Legajo / Categoría'


# --- TU CONFIGURACIÓN ACTUAL DE MODELOS (MANTENIDA Y RESPETADA) ---

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('id_area', 'nombre', 'activo')
    search_fields = ('nombre',)

@admin.register(SubArea)
class SubAreaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'area_padre', 'activo')
    list_filter = ('area_padre', 'activo')
    search_fields = ('nombre',)

@admin.register(Puesto)
class PuestoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'area', 'subarea')
    list_filter = ('area', 'subarea')
    search_fields = ('nombre',) 
    autocomplete_fields = ['area', 'subarea']

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('dni', 'nombre_completo', 'user', 'activo')
    search_fields = ('dni', 'nombre_completo', 'user__username')
    list_filter = ('activo',)
    
@admin.register(OperadorMunicipal)
class OperadorAdmin(admin.ModelAdmin):
    list_display = ('user', 'legajo', 'area', 'subarea', 'puesto', 'rol', 'operador_activo')
    list_filter = ('area', 'subarea', 'rol', 'operador_activo')
    search_fields = ('legajo', 'user__username', 'user__first_name', 'user__last_name')
    
    autocomplete_fields = ['area', 'subarea', 'puesto']
    
    fieldsets = (
        ('Datos de Usuario', {
            'fields': ('user', 'legajo', 'rol')
        }),
        ('Ubicación Laboral', {
            'fields': ('area', 'subarea', 'puesto')
        }),
        ('Estado y Seguridad', {
            'fields': ('operador_activo', 'es_trabajador', 'requiere_cambio_password')
        }),
    )