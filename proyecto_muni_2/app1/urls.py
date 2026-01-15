from django.urls import path, include # type: ignore
from app1 import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler403, handler500

urlpatterns = [
    path('', views.bienvenida, name='bienvenida'),

    # --- PANEL MAESTRO (Permisos) ---
    path('panel-maestro/permisos/', views.gestionar_roles, name='gestionar_roles'),
    

        # Rutas para autenticación
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),


    path('lista_servicios/', views.lista_servicios, name='lista_servicios'),
    path('informacion/', views.informacion, name='informacion'),


        # Rutas para noticias
    path('noticias/', views.lista_noticias, name='lista_noticias'),
    path('noticias/crear/', views.crear_noticia, name='crear_noticia'),
    path('noticias/eliminar/<int:id_noticia>/', views.eliminar_noticia, name='eliminar_noticia'),
    path('noticias/<int:id_noticia>/', views.ver_noticia, name='ver_noticia'),
    path('noticias/<int:id_noticia>/editar/', views.editar_noticia, name='editar_noticia'),

        # Ruta para catastro
    path('catastro_info/', views.catastro_info, name='catastro_info'),
    path('catastro/crear/', views.crear_catastro, name='crear_catastro'),
    path('catastro/listar/', views.listar_catastros, name='listar_catastros'),
    path('catastro/<int:id_catastro>/', views.ver_catastro, name='ver_catastro'),
    path('catastro/<int:id_catastro>/eliminar/', views.eliminar_catastro, name='eliminar_catastro'),
    path('catastros/<int:id_catastro>/editar/', views.editar_catastro, name='editar_catastro'),


    # Rutas para eventos
    path('eventos/', views.eventos, name='eventos'),
    path('eventos/crear/', views.crear_evento, name='crear_evento'),
    path('eventos/editar/<int:id_evento>/', views.editar_evento, name='editar_evento'),
    path('eventos/eliminar/<int:id_evento>/', views.eliminar_evento, name='eliminar_evento'),

    # Ruta sector sociales
    path('sociales/', views.sector_sociales, name='sector_sociales'),
    path('sociales/anses/', views.area_anses, name='area_anses'),
    path('sociales/legales/', views.asuntos_legales, name='asuntos_legales'),
    path('sociales/ninez/', views.ninez_familia, name='ninez_familia'),
    path('sociales/adultos-mayores/', views.adultos_mayores, name='adultos_mayores'),
    path('sociales/seguridad/', views.seguridad_ciudadana, name='seguridad_ciudadana'),

    # Rutas para Eventos Sociales
    path('eventos-sociales/', views.eventos_sociales, name='eventos_sociales'),
    path('eventos-sociales/crear/',views.crear_evento_social,name='crear_evento_social'),
    path('eventos-sociales/editar/<int:id_social>/',views.editar_evento_social,name='editar_evento_social'),
    path('eventos-sociales/eliminar/<int:id_social>/',views.eliminar_evento_social,name='eliminar_evento_social'),
         

    # Rutas para rentas
    path('rentas/', views.renta_info, name='rentas'),
    path("tasas/", views.tasas_municipales, name="tasas"),
    path("regularizaciones/", views.regularizaciones, name="regularizaciones"),


    # ruta para quienes somos

    path('autoridades/', views.autoridades_view, name='autoridades'),
    path('historia/', views.historia, name='historia'),
    path('intendencias/', views.intendencias, name='intendencias'),
    path("organigrama/", views.organigrama, name="organigrama"),

    
  


    # Ruta para consultas sociales
    path('consultas/', views.crear_consulta, name='consultas'),
    path('consultas/ver/', views.ver_consultas, name='ver_consultas'),
    path('consultas/eliminar/<int:id_consulta>/', views.eliminar_consulta, name='eliminar_consulta'),
    path("consultas/ver/<int:id_consulta>/", views.ver_consulta_individual, name="ver_consulta_individual"),


    # ruta contactos


    path('contactos/', views.contactos, name='contactos'),
    path('contacto/ver/<int:contacto_id>/', views.ver_contacto, name='ver_contacto'),
    path('contactos/crear/', views.crear_contacto, name='crear_contacto'),
    path('contactos/editar/<int:contacto_id>/', views.editar_contacto, name='editar_contacto'),
    path('contactos/eliminar/<int:contacto_id>/', views.eliminar_contacto, name='eliminar_contacto'),
    path('papelera/contacto/', views.papelera_contactos, name='papelera_contactos'),
    path('restaurar/<int:contacto_id>/', views.restaurar_contacto, name='restaurar_contacto'),
    path('eliminar-definitivo/contacto/<int:contacto_id>/', views.eliminar_permanente_contacto, name='eliminar_permanente'),




    

    # ruta habilitacion comercial
    path('habilitaciones/bienvenida/',views.bienvenida_habilitaciones,name='bienvenida_habilitaciones'),
    path('habilitaciones/solicitud/',views.solicitar_habilitacion_comercial,name='solicitud_habilitacion'),
    path('habilitaciones/',views.listar_solicitudes_habilitacion,name='listar_solicitudes_habilitacion'),
    path('habilitaciones/<int:id_solicitud>/<str:accion>/', views.gestionar_solicitud_habilitacion, name='gestionar_solicitud_habilitacion'),
    path('habilitaciones/<int:id_solicitud>/',views.ver_solicitud_habilitacion,name='ver_solicitud_habilitacion'),
    path('habilitaciones/crear/', views.crear_solicitud_habilitacion, name='crear_solicitud_habilitacion'),




    # Ruta obligatoria para CKEditor 5
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'app1.views.error_403'
handler500 = 'app1.views.error_500'