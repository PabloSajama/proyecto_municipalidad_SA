from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import ( Noticia, Eventos, Contacto, ConfiguracionSector, AccesoDirecto, ComponenteSector, NotaRecordatorio, ArchivadorImagen)
from users.models import Area, Puesto , SubArea
from django.core.exceptions import ValidationError
from datetime import time, datetime
from django_ckeditor_5.widgets import CKEditor5Widget
from django.forms import inlineformset_factory


class EventoForm(forms.ModelForm):
    class Meta:
        model = Eventos
        fields = ['titulo', 'descripcion', 'lugar', 'fecha', 'imagen']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'lugar': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }




class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        fields = ['nombre_completo', 'area', 'subarea', 'puesto', 'telefono', 'correo', 'imagen']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.Select(attrs={'class': 'form-select', 'onchange': 'this.form.submit();'}), 
            'subarea': forms.Select(attrs={'class': 'form-select'}),
            'puesto': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ContactoForm, self).__init__(*args, **kwargs)
        
        # 1. Filtrado inicial general
        self.fields['area'].queryset = Area.objects.filter(activo=True).order_by('nombre')
        
        # 2. Restricción de Seguridad: Si NO es superuser, lo encerramos en su Área
        if user and not user.is_superuser:
            if hasattr(user, 'operador') and user.operador.area:
                area_user = user.operador.area
                self.fields['area'].queryset = Area.objects.filter(id_area=area_user.id_area)
                self.fields['area'].initial = area_user
                
                # Seteamos el área fija para la lógica de cascada que sigue abajo
                area_id_fijo = area_user.id_area
        else:
            area_id_fijo = None

        # 3. Lógica de cascada corregida para SubÁrea y Puesto
        if 'area' in self.data:
            try:
                area_id = int(self.data.get('area'))
                self.fields['subarea'].queryset = SubArea.objects.filter(area_padre_id=area_id, activo=True).order_by('nombre')
                self.fields['puesto'].queryset = Puesto.objects.filter(area_id=area_id).order_by('nombre')
            except (ValueError, TypeError):
                self.fields['subarea'].queryset = SubArea.objects.none()
                self.fields['puesto'].queryset = Puesto.objects.none()
        elif self.instance.pk and self.instance.area:
            self.fields['subarea'].queryset = SubArea.objects.filter(area_padre=self.instance.area, activo=True).order_by('nombre')
            self.fields['puesto'].queryset = Puesto.objects.filter(area=self.instance.area).order_by('nombre')
        elif area_id_fijo:
            # Si es operador y está creando por primera vez, ve todas las subáreas de SU área
            self.fields['subarea'].queryset = SubArea.objects.filter(area_padre_id=area_id_fijo, activo=True).order_by('nombre')
            self.fields['puesto'].queryset = Puesto.objects.filter(area_id=area_id_fijo).order_by('nombre')
        else:
            self.fields['subarea'].queryset = SubArea.objects.none()
            self.fields['puesto'].queryset = Puesto.objects.none()


            
class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        # Agregamos subarea para que el operador pueda categorizar mejor la noticia
        fields = ['titulo', 'area', 'subarea', 'texto', 'imagen_principal', 'activo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Título...'}),
            'area': forms.Select(attrs={'class': 'form-select'}),
            'subarea': forms.Select(attrs={'class': 'form-select'}),
            'texto': CKEditor5Widget(config_name='default', attrs={'class': 'django_ckeditor_5'}),
            'imagen_principal': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Si el operador no es superusuario, solo puede publicar en su área/subárea
        if user and not user.is_superuser and hasattr(user, 'operador'):
            self.fields['area'].queryset = Area.objects.filter(id_area=user.operador.area.id_area)
            self.fields['area'].initial = user.operador.area
            if user.operador.subarea:
                self.fields['subarea'].queryset = SubArea.objects.filter(id=user.operador.subarea.id)
                self.fields['subarea'].initial = user.operador.subarea

class ConfiguracionSectorForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionSector
        fields = [
            'nombre_pantalla', 'area', 'subarea', 
            'titulo_portal', 'subtitulo_portal', 'descripcion_detallada',
            'url_destino', 'color_destacado', 'color_texto_principal', 'color_iconos',
            'imagen_banner', 'logo_sector',
        ]
        widgets = {
            'area': forms.Select(attrs={'class': 'form-select'}),
            'subarea': forms.Select(attrs={'class': 'form-select'}),
            'nombre_pantalla': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Inicio Sociales'}),
            'titulo_portal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Sector de Rentas'}),
            'subtitulo_portal': forms.TextInput(attrs={'class': 'form-control'}),
            
            # CORREGIDO: Eliminamos el Textarea común y dejamos que use el motor de CKEditor 5
            'descripcion_detallada': CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="extends"),
            
            'url_destino': forms.TextInput(attrs={'class': 'form-control'}),
            'color_destacado': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'color_texto_principal': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'color_iconos': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'imagen_banner': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'logo_sector': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            self.fields['nombre_pantalla'].required = False
            self.fields['nombre_pantalla'].widget.attrs['readonly'] = True
            self.fields['nombre_pantalla'].widget.attrs['class'] = 'form-control bg-light'


class AccesoDirectoForm(forms.ModelForm):
    class Meta:
        model = AccesoDirecto
        fields = ['titulo', 'descripcion', 'url_destino', 'imagen_fondo', 'icono_clase']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Tercera Edad'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Breve descripción...'}),
            'url_destino': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'imagen_fondo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'icono_clase': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'bi-people'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False


class ComponenteSectorForm(forms.ModelForm):
    class Meta:
        model = ComponenteSector
        fields = ['tipo', 'titulo', 'contenido', 'imagen', 'orden'] 
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del bloque'}),
            
            # CORREGIDO: Reemplazamos el Textarea para que los bloques dinámicos también usen CKEditor 5
            'contenido': CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="extends"),
            
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['orden'].widget.attrs['placeholder'] = 'Ej: 1'
        
        # Seteamos todo como no requerido para evitar las validaciones fantasmas en filas vacías del FormSet
        for field in self.fields:
            self.fields[field].required = False

# Nota: En los formularios de Notas e imagenes de notas

class NotaRecordatorioForm(forms.ModelForm):
    class Meta:
        model = NotaRecordatorio
        fields = ['titulo', 'contenido', 'fecha_designada']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Reunión de Hacienda'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalles del recordatorio...'}),
            'fecha_designada': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

# Este es el "archivador" de imágenes que se pega al formulario de la nota
# En portal/forms.py
ImagenNotaFormSet = inlineformset_factory(
    NotaRecordatorio, 
    ArchivadorImagen,
    fields=['imagen'],
    extra=0,
    can_delete=True,
    # Aseguramos que el widget sea correcto
    widgets={'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'})}
)