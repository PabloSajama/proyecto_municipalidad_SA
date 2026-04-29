from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import ( Noticia, Eventos, Contacto, ConfiguracionSector, AccesoDirecto, ComponenteSector, NotaRecordatorio, ArchivadorImagen)
from users.models import Area, Puesto
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
        fields = ['nombre_completo', 'area', 'puesto', 'telefono', 'correo', 'imagen']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.Select(attrs={'class': 'form-select'}),
            'puesto': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Esta línea debe tener sangría (4 espacios)
        user = kwargs.pop('user', None)
        super(ContactoForm, self).__init__(*args, **kwargs)
        self.fields['puesto'].queryset = Puesto.objects.filter(area=user.operador.area)

        # 1. Ajuste de Querysets usando el atributo .nombre
        self.fields['area'].queryset = Area.objects.all().order_by('nombre')
        
        # 2. Lógica de filtrado de Puestos
        if 'area' in self.data:
            try:
                area_id = int(self.data.get('area'))
                self.fields['puesto'].queryset = Puesto.objects.filter(area_id=area_id).order_by('nombre')
            except (ValueError, TypeError):
                self.fields['puesto'].queryset = Puesto.objects.none()
        elif self.instance.pk and self.instance.area:
            # CORRECCIÓN AQUÍ: Usamos .puestos (related_name)
            self.fields['puesto'].queryset = self.instance.area.puestos.all().order_by('nombre')
        else:
            self.fields['puesto'].queryset = Puesto.objects.none()

        # 3. Restricción para no-superusuarios
        if user and not user.is_superuser:
            if hasattr(user, 'perfil') and user.perfil.area:
                area_usuario = user.perfil.area
                self.fields['area'].queryset = Area.objects.filter(id_area=area_usuario.id_area)
                self.fields['area'].initial = area_usuario
                self.fields['puesto'].queryset = area_usuario.puestos.all().order_by('nombre')

class NoticiaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Quitar el pop/requerido si no es estrictamente necesario
        # self.fields['texto'].widget.attrs.pop('required', None)

    class Meta:
        model = Noticia
        fields = ['titulo', 'texto', 'imagen_principal', 'activo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control form-control-lg w-100',
                'placeholder': 'Escribe un título impactante...'
            }),
            # CKEditor5Widget por defecto ya agrega los data-attributes
            'texto': CKEditor5Widget(config_name='default', attrs={'class': 'django_ckeditor_5'}),
            'imagen_principal': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'activo': 'Publicar inmediatamente',
        }

class ConfiguracionSectorForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionSector
        fields = [
            'nombre_pantalla', 
            'titulo_portal', 'subtitulo_portal', 'descripcion_detallada',
            'url_destino',
            'color_destacado', 'color_texto_principal', 'color_iconos',
            'imagen_banner', 'logo_sector',
        ]
        widgets = {
            'nombre_pantalla': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Inicio Sociales'}),
            'titulo_portal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Sector de Rentas'}),
            'subtitulo_portal': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion_detallada': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'url_destino': forms.TextInput(attrs={'class': 'form-control'}),
            'color_destacado': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'color_texto_principal': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'color_iconos': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'imagen_banner': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'logo_sector': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # 1. Quitamos 'user' si es que la vista lo mandó por error a este form
        kwargs.pop('user', None) 
        
        # 2. Llamada correcta al super
        super().__init__(*args, **kwargs)
        
        # 3. Lógica de edición: nombre de pantalla solo lectura
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
        # Hacemos que los campos no sean obligatorios para que el FormSet 
        # ignore la fila vacía extra que aparece al final
        for field in self.fields:
            self.fields[field].required = False

class ComponenteSectorForm(forms.ModelForm):
    class Meta:
        model = ComponenteSector
        fields = ['tipo', 'titulo', 'contenido', 'imagen', 'orden']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del bloque'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Escribe el contenido aquí...'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Esto elimina específicamente el error rosa de "orden" de tu imagen
        self.fields['tipo'].required = False
        self.fields['titulo'].required = False
        self.fields['contenido'].required = False
        self.fields['orden'].required = False
        self.fields['imagen'].required = False
        
        # Atributo extra para guía visual
        self.fields['orden'].widget.attrs['placeholder'] = 'Ej: 1'
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