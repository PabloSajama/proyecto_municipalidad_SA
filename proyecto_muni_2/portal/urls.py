from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.bienvenida, name='bienvenida'),
    path('informacion/', views.informacion, name='informacion'),
    path('servicios/', views.lista_servicios, name='lista_servicios'),


    # quienes somos
    path('autoridades/', views.autoridades_view, name='autoridades'),
    path('historia/', views.historia, name='historia'),
    path('intendencias/', views.intendencias, name='intendencias'),
    path('organigrama/', views.organigrama, name='organigrama'),
    path('sectores/municipales', views.sectores_municipales, name='sectores_municipales'),


    # Eventos
    path('eventos/', views.eventos, name='eventos'),
    path('eventos/crear/', views.crear_evento, name='crear_evento'),
    path('eventos/editar/<int:id_evento>/', views.editar_evento, name='editar_evento'),
    path('eventos/eliminar/<int:id_evento>/', views.eliminar_evento, name='eliminar_evento'),


    # Contactos
    path('contactos/', views.contactos, name='contactos'),
    path('contactos/crear/', views.crear_contacto, name='crear_contacto'),
    path('contactos/editar/<int:contacto_id>/', views.editar_contacto, name='editar_contacto'),
    path('contactos/ver/<int:contacto_id>/', views.ver_contacto, name='ver_contacto'),
    path('contactos/eliminar/<int:contacto_id>/', views.eliminar_contacto, name='eliminar_contacto'),
    path('ajax/load-puestos/', views.ajax_load_puestos, name='ajax_load_puestos'),



    # Noticias
    # --- VISTAS PÚBLICAS (INVITADOS Y VECINOS) ---
    # Listado general de todas las noticias (de mayor a menor ID)
    path('noticias/', views.lista_noticias_publica, name='lista_noticias_publica'),
    # Detalle de la noticia usando el SLUG para URLs amigables
    path('noticia/<slug:slug>/', views.ver_noticia_publica, name='ver_noticia_publica'),
    # --- VISTAS DE GESTIÓN (SOLO OPERADORES LOGUEADOS) ---
    # Panel privado donde el operador ve solo las noticias de su área
    path('gestion/noticias/', views.gestion_noticias, name='gestion_noticias'),
    path('gestion/noticias/publicadas/', views.panel_operador_noticias, name='panel_operador_noticias'),
    path('gestion/noticias/desactivadas/', views.panel_operador_desactivadas, name='panel_operador_desactivadas'),
    # Crear noticia (el área se asigna automáticamente en la vista)
    path('gestion/noticia/nueva/', views.crear_noticia, name='crear_noticia'),
    # Editar noticia (valida que pertenezca al área del operador)
    path('gestion/noticia/editar/<int:id_noticia>/', views.editar_noticia, name='editar_noticia'),
    # Eliminar noticia (borrado lógico: activo=False)
    path('gestion/noticia/eliminar/<int:id_noticia>/', views.eliminar_noticia, name='eliminar_noticia'),
    path('ckeditor5/', include('django_ckeditor_5.urls')),



    #urls para notas e imagenes de notas
    path('notas/', views.lista_notas, name='lista_notas'),
    path('notas/crear/', views.crear_nota_recordatorio, name='crear_nota'),
    path('notas/editar/<int:pk>/', views.editar_nota_recordatorio, name='editar_nota'),
    path('notas/eliminar/<int:pk>/', views.eliminar_nota_logico, name='eliminar_nota_logico'),
    path('notas/ver/nota/<int:pk>/', views.ver_nota_recordatorio, name='ver_nota')
] # Lista vacía por ahora