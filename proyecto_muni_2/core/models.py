# core/models.py
from django.db import models
from django.conf import settings

class RegistroBase(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)

    class Meta:
        abstract = True

class HistorialVersiones(models.Model):
    ESTADOS = [('PENDIENTE', 'Pendiente'), ('APROBADO', 'Aprobado'), ('RECHAZADO', 'Rechazado')]
    
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    tabla = models.CharField(max_length=100)
    registro_id = models.PositiveIntegerField(null=True, blank=True)
    accion = models.CharField(max_length=10) # CREAR, EDITAR, ELIMINAR
    
    datos_anteriores = models.JSONField(null=True, blank=True)
    datos_nuevos = models.JSONField(null=True, blank=True)
    
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')
    revisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='revisiones_aprobadas'
    )
    comentario_revision = models.TextField(null=True, blank=True)