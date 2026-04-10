from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Perfil

class RegistroCompletoForm(UserCreationForm):
    # Campos del User (para que el Admin de Django se vea como en tu foto)
    first_name = forms.CharField(label="Nombre", required=True)
    last_name = forms.CharField(label="Apellido", required=True)
    email = forms.CharField(label="Correo Electrónico", required=True)
    
    # Campos del Perfil (ejemplo: DNI y Teléfono)
    dni = forms.CharField(label="DNI", max_length=20, required=True)
    telefono = forms.CharField(label="Teléfono", max_length=20, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        # Añadimos los campos de User al formulario
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def save(self, commit=True):
        # 1. Guardamos el usuario primero
        user = super().save(commit=commit)
        if commit:
            # 2. Creamos o actualizamos el perfil con los datos extra
            Perfil.objects.update_or_create(
                user=user,
                defaults={
                    'dni': self.cleaned_data.get('dni'),
                    'telefono': self.cleaned_data.get('telefono'),
                }
            )
        return user