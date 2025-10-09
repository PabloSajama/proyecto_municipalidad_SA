# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ArchivosCatastro(models.Model):
    id_archivo_catastro = models.AutoField(primary_key=True)
    id_catastro = models.ForeignKey('Catastros', models.DO_NOTHING, db_column='id_catastro')
    archivo = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    fecha_subida = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'archivos_catastro'


class ArchivosRenta(models.Model):
    id_archivo_renta = models.AutoField(primary_key=True)
    id_renta = models.ForeignKey('Rentas', models.DO_NOTHING, db_column='id_renta')
    archivo = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    fecha_subida = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'archivos_renta'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Catastros(models.Model):
    id_catastro = models.AutoField(primary_key=True)
    dni_propietario = models.CharField(max_length=15)
    nombre_propietario = models.CharField(max_length=100, blank=True, null=True)
    numero_catastro = models.CharField(max_length=50)
    observaciones = models.TextField(blank=True, null=True)
    eliminado = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='catastros/', blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'catastros'
        unique_together = (('dni_propietario', 'numero_catastro'),)
        # managed = False ← Esto lo quitamos o lo cambiamos a True



class Comentario(models.Model):
    id_comentario = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    noticia = models.ForeignKey('Noticia', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Noticia relacionada")
    evento = models.ForeignKey('Eventos', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Evento relacionado")
    comentario = models.TextField(verbose_name="Comentario")
    fecha_comentario = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del comentario")

    class Meta:
        db_table = 'comentarios'
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ['-fecha_comentario']
        managed = True

    def __str__(self):
        return f"Comentario de {self.user.username} - {self.fecha_comentario.strftime('%Y-%m-%d %H:%M')}"

class ConsultasSociales(models.Model):
    id_consulta = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.DO_NOTHING)
    asunto = models.CharField(max_length=255)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'consultas_sociales'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'

class Eventos(models.Model):
    id_evento = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='eventos/', blank=True, null=True)
    fecha_evento = models.DateField()
    fecha_publicacion = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'eventos'


class HabilitacionesComerciales(models.Model):
    id_habilitacion = models.AutoField(primary_key=True)
    razon_social = models.CharField(max_length=255)
    cuit = models.CharField(max_length=20)
    direccion_comercial = models.TextField()
    rubro = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=9, blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'habilitaciones_comerciales'


class Noticia(models.Model):
    id_noticia = models.AutoField(primary_key=True)
    titulo = models.CharField("Título", max_length=255)
    texto = models.TextField("Texto", db_column='contenido')  # Mapeo contenido -> texto
    imagen_principal = models.ImageField("Imagen Principal", upload_to='noticias/', blank=True, null=True, db_column='imagen')
    fecha_publicacion = models.DateField("Fecha de Publicacion", auto_now_add=True, null=True, blank=True, db_column='fecha_publicacion')
    user = models.ForeignKey(User, models.DO_NOTHING, verbose_name="Autor", blank=True, null=True, db_column='user_id')
    activo = models.BooleanField(default=True) 

    class Meta:
        db_table = 'noticias'
        verbose_name = "Noticia"
        verbose_name_plural = "Noticias"
        managed = True

    def __str__(self):
        return f"{self.titulo} (ID: {self.id_noticia})"


class Perfil(models.Model):
    id_perfil = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dni = models.CharField(unique=True, max_length=15)
    nombre_completo = models.CharField(max_length=255)
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    ROL_CHOICES = [
        ('visitante', 'Visitante'),
        ('administrador', 'Administrador'),
    ]
    rol = models.CharField(
        max_length=13,
        choices=ROL_CHOICES,
        default='visitante'
    )

    def __str__(self):
        return f"{self.nombre_completo} ({self.dni})"

    class Meta:
        db_table = 'perfil'



class Rentas(models.Model):
    id_renta = models.AutoField(primary_key=True)
    dni_contribuyente = models.CharField(max_length=15)
    numero_renta = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.CharField(max_length=255, blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rentas'
        unique_together = (('dni_contribuyente', 'numero_renta'),)

class Contacto(models.Model):
    id_contacto = models.AutoField(primary_key=True)  # ID explícito
    nombre_completo = models.CharField(max_length=255)
    puesto = models.CharField(max_length=100)
    descripcion = models.TextField()
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()
    imagen = models.ImageField(upload_to='contacto/', null=True, blank=True)

    class Meta:
        db_table = 'contacto'  # Nombre real de la tabla

    def __str__(self):
        return self.nombre_completo