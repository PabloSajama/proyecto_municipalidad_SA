from django.db import models
from core.models import RegistroBase
from django.conf import settings
from users.models import Area , SubArea
from django.core.exceptions import PermissionDenied

class ConsultasSociales(models.Model):
    id_consulta = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mis_consultas')
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    area_destino = models.ForeignKey(
        Area, 
        on_delete=models.CASCADE, null=True, blank=True, # PROTECT evita borrar un área si tiene reclamos asociados
        related_name='consultas_recibidas',
        verbose_name="Área de destino"
    )
    # --- NUEVO CAMPO ---
    subarea_destino = models.ForeignKey(
        SubArea,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='consultas_recibidas',
        verbose_name="Sub-Área de destino"
    )
    respondida = models.BooleanField(default=False)
    respuesta_municipio = models.TextField(blank=True, null=True)
    fecha_respuesta = models.DateTimeField(blank=True, null=True)
    class Meta:
        ordering = ['-fecha_envio']
    def __str__(self):
        return f"Consulta #{self.id_consulta} - {self.area_destino}"

class EventosSociales(RegistroBase):
    id_social = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200) # Ej: Boda en el Prado
    descripcion = models.TextField()
    lugar = models.CharField(max_length=255)
    fecha_hora = models.DateTimeField()
    imagen = models.ImageField(upload_to='social/eventos/', null=True, blank=True)
    activo = models.BooleanField(default=True, verbose_name="Estado Activo")
    area = models.ForeignKey(
        'users.Area', 
        on_delete=models.CASCADE, 
        related_name='eventos_sociales',
        null=True, blank=True
    )
    subarea = models.ForeignKey(
        'users.SubArea', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='eventos_sociales'
    )

# Modelo para Reclamos
class Reclamo(models.Model):
    id_reclamo = models.AutoField(primary_key=True, editable=False)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mis_reclamos')
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    area_destino = models.ForeignKey(
        Area, 
        on_delete=models.CASCADE, null=True, blank=True, # PROTECT evita borrar un área si tiene reclamos asociados
        related_name='reclamos_recibidos',
        verbose_name="Área de destino"
    )
    # --- NUEVO CAMPO ---
    subarea_destino = models.ForeignKey(
        SubArea,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reclamos_recibidos',
        verbose_name="Sub-Área de destino"
    )
    # --- Campos para la Gestión del Operador ---
    respondido = models.BooleanField(default=False)
    respuesta_municipio = models.TextField(blank=True, null=True)
    fecha_respuesta = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-fecha_envio']
    def __str__(self):
        return f"Reclamo #{self.id_reclamo} - {self.area_destino}"