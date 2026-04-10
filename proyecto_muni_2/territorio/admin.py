from django.contrib import admin
from .models import Catastros, ArchivosCatastro

class ArchivosInline(admin.TabularInline):
    model = ArchivosCatastro
    extra = 1

@admin.register(Catastros)
class CatastrosAdmin(admin.ModelAdmin):
    list_display = ('numero_catastro', 'propietario', 'direccion_inmueble', 'activo')
    search_fields = ('numero_catastro', 'propietario__dni', 'direccion_inmueble')
    inlines = [ArchivosInline]