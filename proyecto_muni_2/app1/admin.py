from django.contrib import admin # type: ignore
from .models import Noticia,  Perfil, Catastros,Eventos, ConsultasSociales, Contacto # Importá tu modelo
from django.forms.models import model_to_dict

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields]
    
@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields]
    
@admin.register(Catastros)
class CatastroAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields]
    
@admin.register(Eventos)
class CatastroAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields]
    
@admin.register(ConsultasSociales)
class CatastroAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields]
    
@admin.register(Contacto)
class CatastroAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields]