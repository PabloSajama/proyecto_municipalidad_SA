from django.db import models
from core.models import RegistroBase
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify

class Noticia(RegistroBase):
    id_noticia = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=255)
    # Relacionamos con las áreas definidas en la app 'users'
    area = models.ForeignKey('users.Area', on_delete=models.SET_NULL, null=True)
    texto = CKEditor5Field('Contenido', config_name='default')
    imagen_principal = models.ImageField(upload_to='noticias/', null=True, blank=True)
    autor = models.ForeignKey('users.OperadorMunicipal', on_delete=models.SET_NULL, null=True)
    activo = models.BooleanField(default=True) # Para borrado lógico
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    # Dentro de class Noticia(models.Model):
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.titulo)
            slug = base_slug
            counter = 1

            while Noticia.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

class Eventos(RegistroBase):
    id_evento = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Creado por")
    titulo = models.CharField(max_length=200, verbose_name="Título del Evento")
    descripcion = models.TextField(verbose_name="Descripción")
    lugar = models.CharField(max_length=255, verbose_name="Lugar")
    fecha = models.DateField(verbose_name="Fecha del Evento")
    fecha = models.DateField(default=timezone.now, verbose_name="Fecha del Evento")
    imagen = models.ImageField(upload_to='eventos/', null=True, blank=True, verbose_name="Imagen")
    activo = models.BooleanField(default=True) # Para borrado lógico

    class Meta:
        db_table = 'eventos'
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['-fecha']

    def __str__(self):
        return self.titulo


class HistorialActividadEvento(models.Model):
    id_historial = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")
    accion = models.CharField(max_length=50, verbose_name="Acción") # CREAR, EDITAR, ELIMINAR
    tabla = models.CharField(max_length=50, default="EVENTOS", verbose_name="Módulo")
    
    # Referencia técnica al ID del evento (sin ser FK rígida)
    objeto_id = models.IntegerField(null=True, blank=True, verbose_name="ID del Objeto")
    
    info_operador = models.TextField(verbose_name="Detalles del Movimiento")

    class Meta:
        db_table = 'historial_actividad_evento'
        verbose_name = "Historial de Actividad"
        verbose_name_plural = "Historial de Actividades"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.user.username} - {self.accion} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"

class Contacto(models.Model):
    id_contacto = models.AutoField(primary_key=True)
    nombre_completo = models.CharField(max_length=255)
    
    # Conexión a la app 'users'
    area = models.ForeignKey('users.Area', on_delete=models.CASCADE, related_name='contactos_portal')
    puesto = models.ForeignKey('users.Puesto', on_delete=models.CASCADE, related_name='contactos_portal')
    
    telefono = models.CharField(max_length=50)
    correo = models.EmailField()
    imagen = models.ImageField(upload_to='contactos/', null=True, blank=True)
    
    activo = models.BooleanField(default=True)
    
    # Campos de auditoría que pide tu vista
    creado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='contactos_creados')
    ultima_modificacion_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='contactos_modificados')
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre_completo
# Añade esto dentro de la clase Contacto
    def save(self, *args, **kwargs):
        # Aquí podrías agregar lógica extra si fuera necesario, 
        # pero la mayoría de la auditoría la manejaremos en la Vista 
        # para capturar al request.user fácilmente.
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'contactos'
        verbose_name = "Contacto del Portal"
        verbose_name_plural = "Contactos del Portal"



class ConfiguracionSector(RegistroBase):
    area = models.ForeignKey('users.Area', on_delete=models.CASCADE, related_name='configuraciones_web')
    slug_pantalla = models.SlugField(max_length=100)
    nombre_pantalla = models.CharField(max_length=100)

    # Datos base fijos (La cabecera no suele cambiar de lugar)
    titulo_portal = models.CharField(max_length=200)
    subtitulo_portal = models.CharField(max_length=255, blank=True, null=True)
    descripcion_detallada = models.TextField(blank=True, null=True) # Descripción base
    
    # Estética
    color_destacado = models.CharField(max_length=7, default="#1a2a40")
    color_texto_principal = models.CharField(max_length=7, default="#ffffff")
    color_iconos = models.CharField(max_length=7, default="#1a2a40")

    # Imágenes principales
    imagen_banner = models.ImageField(upload_to='sectores/banners/', blank=True, null=True)
    logo_sector = models.ImageField(upload_to='sectores/logos/', blank=True, null=True)

    # URL fija (si aplica)
    url_destino = models.CharField(max_length=100, blank=True) 

    class Meta:
        db_table = 'configuracion_sectores'
        unique_together = ('area', 'slug_pantalla')

# --- ESTE ES EL NUEVO MODELO QUE REEMPLAZA LOS "EXTRA_TITULO_X" ---
class ComponenteSector(models.Model):
    TIPOS = [
        ('texto', 'Bloque de Texto'),
        ('imagen', 'Imagen Destacada'),
        ('video', 'Video (Link)'),
        ('contacto', 'Ficha de Contacto'), # Para mover el contacto de lugar
    ]
    
    configuracion = models.ForeignKey(ConfiguracionSector, on_delete=models.CASCADE, related_name='componentes')
    tipo = models.CharField(max_length=20, choices=TIPOS, default='texto')
    titulo = models.CharField(max_length=255, blank=True, null=True)
    contenido = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='sectores/componentes/', blank=True, null=True)
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True, null=True, blank=True)

    class Meta:
        ordering = ['orden']

class AccesoDirecto(models.Model):
    # (Este modelo se queda igual, ya que son los botones finales de la página)
    configuracion = models.ForeignKey(ConfiguracionSector, on_delete=models.CASCADE, related_name='accesos')
    titulo = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True)
    url_destino = models.URLField(max_length=255)
    imagen_fondo = models.ImageField(upload_to='sectores/accesos/', blank=True, null=True)
    icono_clase = models.CharField(max_length=50, default="bi-link")
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['orden']

# Nota: En los formularios de Notas e imagenes de notas, hacemos que los campos no sean obligatorios para que el FormSet ignore la fila vacía extra que aparece al final. Esto se maneja en el __init__ de cada form correspondiente.   
class NotaRecordatorio(models.Model):
    # Relación con el usuario (trabajador o vecino)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mis_notas')
    
    # Contenido de la nota
    titulo = models.CharField(max_length=200, verbose_name="Título del Recordatorio")
    contenido = models.TextField(verbose_name="Descripción o Nota", blank=True, null=True)
    
    # Fechas solicitadas
    fecha_actual = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_designada = models.DateTimeField(verbose_name="Fecha del Recordatorio", help_text="Fecha en la que debe cumplirse el recordatorio")
    
    # Borrado lógico (activo por defecto)
    activo = models.BooleanField(default=True, verbose_name="Estado Activo")
    
    # Opcional: para marcar si la tarea ya se hizo
    completada = models.BooleanField(default=False, verbose_name="¿Completada?")

    class Meta:
        verbose_name = "Nota y Recordatorio"
        verbose_name_plural = "Notas y Recordatorios"
        ordering = ['-fecha_designada']

    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"

class ArchivadorImagen(models.Model):
    """
    Tabla separada para las imágenes, permitiendo que una nota 
    tenga varias fotos asociadas.
    """
    nota = models.ForeignKey(NotaRecordatorio, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='notas/evidencias/%Y/%m/%d/', verbose_name="Imagen Adjunta")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Imagen de Nota"
        verbose_name_plural = "Archivador de Imágenes"

    def __str__(self):
        return f"Imagen para: {self.nota.titulo}"