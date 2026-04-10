from django.db import models
from core.models import RegistroBase

class Catastros(RegistroBase):
    id_catastro = models.AutoField(primary_key=True)
    # Relación con el Perfil de la app users
    propietario = models.ForeignKey('users.Perfil', on_delete=models.CASCADE, related_name='propiedades')
    numero_catastro = models.CharField(max_length=50, unique=True, verbose_name="Número de Catastro / Padrón")
    nomenclatura = models.CharField(max_length=100, blank=True, help_text="Datos técnicos del lote/manzana")
    direccion_inmueble = models.CharField(max_length=255)
    observaciones = models.TextField(blank=True)
    eliminado = models.BooleanField(default=False)

    def __str__(self):
        return f"Catastro {self.numero_catastro} - {self.direccion_inmueble}"

    class Meta:
        verbose_name = "Catastro"
        verbose_name_plural = "Catastros"

class ArchivosCatastro(models.Model):
    id_archivo = models.AutoField(primary_key=True)
    # Un catastro puede tener muchos archivos (Planos, Escrituras, Fotos)
    catastro = models.ForeignKey(Catastros, on_delete=models.CASCADE, related_name='documentos')
    titulo = models.CharField(max_length=100, help_text="Ej: Plano de Mensura, Escritura PDF")
    archivo = models.FileField(upload_to='territorio/documentos/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} - {self.catastro.numero_catastro}"