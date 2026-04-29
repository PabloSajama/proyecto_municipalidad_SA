# users/models.py
from django.db import models
from django.contrib.auth.models import User
from core.models import RegistroBase  # Importamos la base de core

class Area(RegistroBase):
    id_area = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    def __str__(self): return self.nombre



class Puesto(RegistroBase):
    id_puesto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='puestos')
    def __str__(self): return f"{self.nombre} ({self.area.nombre})"

class RolMunicipal(models.TextChoices):
    OPERADOR = 'OPERADOR', 'Operador (Crear/Editar)'
    ADMINISTRADOR = 'ADMIN', 'Administrador (Crear/Editar/Eliminar)'
    SUPER_USUARIO = 'SUPER', 'Súper Usuario (Control Total)'

class OperadorMunicipal(RegistroBase):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='operador')
    legajo = models.CharField(max_length=20, unique=True)
    area = models.ForeignKey(Area, on_delete=models.PROTECT)
    puesto = models.ForeignKey(Puesto, on_delete=models.PROTECT)
    rol = models.CharField(max_length=10, choices=RolMunicipal.choices, default=RolMunicipal.OPERADOR)
    operador_activo = models.BooleanField(default=True)
    # El atributo que definimos para bloquear la creación de perfil
    es_trabajador = models.BooleanField(default=True)
    requiere_cambio_password = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.rol})"

# users/models.py

class Perfil(models.Model): # <--- Cambio de RegistroBase a models.Model
    # Campos que antes venían de RegistroBase (los ponemos manual para que Django los vea claro)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    # Tus campos de siempre
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    dni = models.CharField(max_length=15, unique=True)
    nombre_completo = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.nombre_completo})"