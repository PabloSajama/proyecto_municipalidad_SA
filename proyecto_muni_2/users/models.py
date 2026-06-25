# users/models.py
from django.db import models
from django.contrib.auth.models import User
from core.models import RegistroBase  # Importamos la base de core

class Area(RegistroBase):
    id_area = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True, verbose_name="Área Activa")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Área"
        verbose_name_plural = "Áreas"
        ordering = ['nombre']


class SubArea(RegistroBase):
    id_subarea = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    area_padre = models.ForeignKey(
        Area, 
        on_delete=models.CASCADE, 
        related_name='subareas',
        verbose_name="Área Superior"
    )
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True, verbose_name="¿Sub-Área Activa?")

    class Meta:
        verbose_name = "Sub-Área"
        verbose_name_plural = "Sub-Áreas"
        unique_together = ('nombre', 'area_padre')
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.area_padre.nombre})"

class Puesto(RegistroBase):
    id_puesto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='puestos')
    subarea = models.ForeignKey(SubArea, on_delete=models.SET_NULL, null=True, blank=True, related_name='puestos')
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
    subarea = models.ForeignKey(SubArea, on_delete=models.SET_NULL, null=True, blank=True, related_name='operadores')

    def __str__(self):
        return f"{self.user.username} ({self.rol})"

# users/models.py

class Perfil(models.Model):
    # Campos base manuales para control de auditoría
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    # Relación uno a uno nativa de Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    
    # Atributos del Perfil
    dni = models.CharField(max_length=15, unique=True)
    nombre_completo = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=20, blank=True)

    # MODIFICADO: Añadimos soporte para almacenar las imágenes de perfil
    foto_perfil = models.ImageField(upload_to='perfiles/fotos/', blank=True, null=True, verbose_name="Foto de Perfil")

    def __str__(self):
        return f"{self.user.username} ({self.nombre_completo})"