from django.urls import path # type: ignore
from app1 import views

urlpatterns = [
    path('', views.bienvenida, name='bienvenida'),

        # Rutas para autenticación
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),


    path('contactos/', views.contactos, name='contactos'),
    path('lista_servicios/', views.lista_servicios, name='lista_servicios'),
    path('informacion/', views.informacion, name='informacion'),


        # Rutas para noticias
    path('noticias/', views.lista_noticias, name='lista_noticias'),
    path('noticias/crear/', views.crear_noticia, name='crear_noticia'),
    path('noticias/eliminar/<int:id_noticia>/', views.eliminar_noticia, name='eliminar_noticia'),
    path('noticia/<int:noticia_id>/', views.ver_noticia, name='ver_noticia'),

        # Ruta para catastro
    path('catastro_info/', views.catastro_info, name='catastro_info'),
    path('catastro/buscar/', views.buscar_catastro, name='buscar_catastro'),
    path('catastro/crear/', views.crear_catastro, name='crear_catastro'),
    path('catastro/listar/', views.listar_catastros, name='listar_catastros'),
    
]