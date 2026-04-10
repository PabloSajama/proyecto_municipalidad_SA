from django.db import models
from core.models import RegistroBase

class Rentas(RegistroBase):
    id_renta = models.AutoField(primary_key=True)
    perfil = models.ForeignKey('users.Perfil', on_delete=models.CASCADE, related_name='rentas')
    tipo_tasa = models.CharField(max_length=100) # Ej: Inmobiliario, Automotor
    monto_deuda = models.DecimalField(max_digits=12, decimal_places=2)
    pagado = models.BooleanField(default=False)

class ArchivosRenta(models.Model):
    renta = models.ForeignKey(Rentas, on_delete=models.CASCADE, related_name='comprobantes')
    archivo = models.FileField(upload_to='hacienda/comprobantes/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

class SolicitudHabilitacionComercial(RegistroBase):
    ESTADOS = [('pendiente', 'Pendiente'), ('aprobada', 'Aprobada'), ('rechazada', 'Rechazada')]
    
    id_solicitud = models.AutoField(primary_key=True)
    nombre_comercio = models.CharField(max_length=200)
    rubro = models.CharField(max_length=100)
    cuit = models.CharField(max_length=20)
    direccion_local = models.CharField(max_length=255)
    
    # Datos de control
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    observacion_admin = models.TextField(blank=True)
    aprobado_por = models.ForeignKey('users.OperadorMunicipal', on_delete=models.SET_NULL, null=True, blank=True)