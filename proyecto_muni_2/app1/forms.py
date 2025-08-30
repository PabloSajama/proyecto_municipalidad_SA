from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from app1.models import Perfil, Noticia, Catastros
from django.core.exceptions import ValidationError


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




## Formulario para Noticias
class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = ['titulo', 'texto', 'imagen_principal']  # usa nombres del modelo, no de la BD
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'texto': forms.Textarea(attrs={'class': 'form-control'}),
            'imagen_principal': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }




# Formulario para Catastro
class CatastroForm(forms.ModelForm):
    class Meta:
        model = Catastros
        exclude = ['eliminado']
        widgets = {
            'fecha_registro': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        dni = cleaned_data.get('dni_propietario')
        numero = cleaned_data.get('numero_catastro')

        if Catastros.objects.filter(dni_propietario=dni, numero_catastro=numero, eliminado=False).exists():
            raise forms.ValidationError("Ya existe un catastro con este DNI y número.")

        return cleaned_data