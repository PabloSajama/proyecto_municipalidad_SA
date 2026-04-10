from django.urls import path
from . import views

# El namespace debe ser 'social' para que los templates 
# funcionen con {% url 'social:nombre' %}
app_name = 'social'

urlpatterns = [
    
    path('inicio-social/', views.inicio_social, name='inicio-social'),
    # ==========================================================
    # VISTAS PÚBLICAS (CALENDARIO)
    # ==========================================================
    # Ruta principal: Muestra el calendario con FullCalendar
    path('agenda/', views.lista_eventos_sociales, name='lista_eventos'),
    

    # ==========================================================
    # GESTIÓN ADMINISTRATIVA (OPERADORES)
    # ==========================================================
    # Crear un nuevo evento social
    path('gestion/nuevo/', views.crear_evento_social, name='crear_evento'),
    
    # Editar un evento (el <int:id_social> es capturado por la vista)
    path('gestion/editar/<int:id_social>/', views.editar_evento_social, name='editar_evento'),
    
    # Borrado lógico del evento
    path('gestion/eliminar/<int:id_social>/', views.eliminar_evento_social, name='eliminar_evento'),



    #url consultas sociales
    path('consultas/crear/', views.crear_consulta, name='crear_consulta'),
    path('consultas/', views.lista_consultas, name='lista_consultas'),
    path('consultas/ver/<int:id_consulta>/', views.ver_consulta, name='ver_consulta'),
    path('consultas/borrar/<int:id_consulta>/', views.borrar_logico_consulta, name='borrar_logico_consulta'),


    path('mis-consultas/', views.mis_consultas, name='mis-consultas'),
    path('mi-consulta/<int:id_consulta>/', views.ver_consulta_personal, name='ver_consulta_personal'),



    # Vista para el Ciudadano (Crear y ver sus propios reclamos)
    path('reclamos/nuevo/', views.crear_reclamo, name='crear_reclamo'),
    path('mis_reclamos/', views.mis_reclamos, name='mis_reclamos'),
    path('mi-reclamo/<int:id_reclamo>/', views.ver_reclamo_personal, name='ver_reclamo_personal'),

    # Vista para el Operador (Gestión y respuesta)
    path('lista_reclamos/', views.lista_reclamos, name='lista_reclamos'),
    path('operador/reclamo/<int:id_reclamo>/', views.ver_reclamo, name='ver_reclamo'),
    path('operador/reclamo/archivar/<int:id_reclamo>/', views.borrar_logico_reclamo, name='borrar_logico_reclamo'),
    
]