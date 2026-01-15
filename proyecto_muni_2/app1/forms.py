from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from app1.models import Perfil, Noticia, Catastros , Eventos, Contacto, ConsultasSociales , SolicitudHabilitacionComercial, EventosSociales
from django.core.exceptions import ValidationError
from datetime import time, timedelta


# Formulario para Registro de Usuarios
class RegistroForm(UserCreationForm):
    username = forms.CharField(
        label='Nombre de usuario',
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese su nombre de usuario',
            'autocomplete': 'username'
        })
    )
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: ejemplo@correo.com'
        })
    )
    first_name = forms.CharField(
        label='Nombre',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese su nombre'})
    )
    last_name = forms.CharField(
        label='Apellido',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese su apellido'})
    )

    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingrese una contraseña segura'})
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repita la contraseña'})
    )

    dni = forms.CharField(
        label='DNI',
        max_length=15,
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese su DNI'})
    )
    direccion = forms.CharField(
        label='Dirección',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese su dirección',
            'style': 'resize:none;'  # evita que el usuario modifique tamaño (aunque es input text no textarea)
        })
    )
    telefono = forms.CharField(
        label='Teléfono',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese su teléfono'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'dni', 'direccion', 'telefono')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo ya está registrado.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            Perfil.objects.create(
                user=user,
                dni=self.cleaned_data['dni'],
                direccion=self.cleaned_data['direccion'],
                telefono=self.cleaned_data['telefono'],
                rol='visitante'
            )
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Ingrese su usuario'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingrese su contraseña'})
    )



class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = ['titulo', 'sector', 'texto', 'imagen_principal', 'activo']
        
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el título de la noticia'
            }),
            'sector': forms.Select(attrs={
                'class': 'form-select'
            }),
            'imagen_principal': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            # Cambiamos CheckboxInput por HiddenInput para ocultarlo del usuario
            'activo': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super(NoticiaForm, self).__init__(*args, **kwargs)
        
        # CKEditor5 maneja su propio renderizado
        self.fields['texto'].required = False
        self.fields['sector'].empty_label = "Seleccione un sector..."
        
        # Forzamos que el valor inicial sea True si es un formulario nuevo
        if not self.instance.pk:
            self.initial['activo'] = True

            

# Formulario para Catastro
class CatastroForm(forms.ModelForm):
    class Meta:
        model = Catastros
        exclude = ['eliminado']
        widgets = {
            'fecha_registro': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'campo-input'
            }),
            'dni_propietario': forms.TextInput(attrs={'class': 'campo-input'}),
            'nombre_propietario': forms.TextInput(attrs={'class': 'campo-input'}),
            'numero_catastro': forms.TextInput(attrs={'class': 'campo-input'}),
            'observaciones': forms.Textarea(attrs={'class': 'campo-textarea', 'rows': 4}),
            
        }

    def clean(self):
        cleaned_data = super().clean()
        dni = cleaned_data.get('dni_propietario')
        numero = cleaned_data.get('numero_catastro')
        catastro_id = self.instance.pk

        if Catastros.objects.filter(
            dni_propietario=dni,
            numero_catastro=numero,
            eliminado=False
        ).exclude(pk=catastro_id).exists():
            raise forms.ValidationError("Ya existe un catastro con este DNI y número.")

        return cleaned_data



#formulario eventos


# ---------- FORMULARIO ----------
class EventoForm(forms.ModelForm):
    class Meta:
        model = Eventos
        fields = ['titulo', 'descripcion', 'imagen', 'fecha_evento']
        widgets = {
            'fecha_evento': forms.DateInput(attrs={'type': 'date'}),
        }



# Formulario para Contacto
class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        # Solo campos editables manualmente
        fields = ['nombre_completo', 'puesto', 'area', 'descripcion', 'telefono', 'correo', 'imagen']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'puesto': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ContactoForm, self).__init__(*args, **kwargs)

        if user:
            # Superusuario ve todo, operadores ven solo su área
            if not user.is_superuser:
                mapeo = {'SOCIAL': 'SOCIAL', 'RENTAS': 'HACIENDA', 'CATASTRO': 'CATASTRO'}
                mi_area = mapeo.get(user.perfil.area, 'GENERAL')

                self.fields['area'].choices = [
                    (cod, nombre) for cod, nombre in Contacto.AREAS_CHOICES if cod == mi_area
                ]
                self.fields['area'].initial = mi_area


# Formulario para Consultas Sociales
class SolicitudHabilitacionForm(forms.ModelForm):
    class Meta:
        model = SolicitudHabilitacionComercial
        exclude = ['estado', 'observacion_admin', 'fecha_solicitud']





# formulario eventos sociales
class EventoSocialForm(forms.ModelForm):
    # Generamos las opciones de 30 min (de 06:00 a 23:00)
    HORAS_CHOICES = [
        (time(h, m).strftime('%H:%M'), time(h, m).strftime('%H:%M'))
        for h in range(6, 23) 
        for m in (0, 30)
    ]

    # Campos extra que no están en el modelo pero usaremos para construir la fecha completa
    fecha = forms.DateField(
        label="Fecha del Evento",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    hora = forms.ChoiceField(
        label="Hora de Inicio (Bloques de 30 min)",
        choices=HORAS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = EventosSociales
        fields = [
            'titulo', 
            'descripcion', 
            'imagen', 
            'lugar'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Boda de Juan y Ana'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Breve descripción...'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Salón Municipal'}),
        }

    def __init__(self, *args, **kwargs):
        super(EventoSocialForm, self).__init__(*args, **kwargs)
        # Si estamos editando, precargamos la fecha y hora desde el campo fecha_evento
        if self.instance and self.instance.fecha_evento:
            self.fields['fecha'].initial = self.instance.fecha_evento.date()
            self.fields['hora'].initial = self.instance.fecha_evento.strftime('%H:%M')