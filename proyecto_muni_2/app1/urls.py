from django.urls import path # type: ignore
from app1 import views

urlpatterns = [
    path('', views.bienvenida, name='bienvenida'),

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
    path('eventos/editar/<int:evento_id>/', views.editar_evento, name='editar_evento'),
    path('eventos/eliminar/<int:evento_id>/', views.eliminar_evento, name='eliminar_evento'),


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
    path('contactos/eliminar/<int:contacto_id>/', views.eliminar_contacto, name='eliminar_contacto'),
    
]