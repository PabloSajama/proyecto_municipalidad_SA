from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Perfil
from django.contrib.auth.forms import PasswordResetForm

class RegistroCompletoForm(UserCreationForm):
    # Campos del User nativo adaptados a Bootstrap
    first_name = forms.CharField(label="Nombre", required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Apellido", required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Correo Electrónico", required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    # Campos que van directo a tu extensión de Perfil
    dni = forms.CharField(label="DNI", max_length=15, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(label="Teléfono", max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    direccion = forms.CharField(label="Dirección", max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def save(self, commit=True):
        # Guardamos primero las credenciales del usuario base de Django
        user = super().save(commit=commit)
        
        if commit:
            # Capturamos y sanitizamos nombre y apellido
            first = self.cleaned_data.get('first_name', '').strip()
            last = self.cleaned_data.get('last_name', '').strip()
            
            # Concatenamos de forma automática para poblar tu atributo único del modelo
            nombre_armado = f"{first} {last}".strip()
            
            # Creamos el registro del perfil en cascada
            Perfil.objects.update_or_create(
                user=user,
                defaults={
                    'dni': self.cleaned_data.get('dni'),
                    'nombre_completo': nombre_armado,
                    'telefono': self.cleaned_data.get('telefono'),
                    'direccion': self.cleaned_data.get('direccion'),
                    # El registro inicial inicia sin foto por defecto
                }
            )
        return user


# ==========================================
# 2. FORMULARIO DE EDICIÓN (Para el Panel)
# ==========================================
class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        # Especificamos los campos que el usuario puede retocar autónomamente
        fields = ['nombre_completo', 'dni', 'telefono', 'direccion', 'foto_perfil']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan Carlos Pérez'}),
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_perfil': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre_completo': 'Nombre Completo',
            'dni': 'DNI',
            'telefono': 'Teléfono de Contacto',
            'direccion': 'Dirección Residencial',
            'foto_perfil': 'Foto de Perfil',
        }


class OlvidePasswordForm(PasswordResetForm):
    email = forms.EmailField(
        label="Correo Electrónico",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ejemplo@municipio.com',
            'required': 'true'
        })
    )