from django.urls import path
from . import views

urlpatterns = [
    # Gestión Interna
    path('panel-superior/', views.admin_superior_panel, name='admin_superior_panel'),
    path('ver-usuario-operador/<int:user_id>/', views.ver_usuario_operador, name='ver_usuario_operador'),


    ##cambiar contraseña operador municipal
    path('cambiar-password/', views.cambiar_password_operador, name='cambiar_password_operador'),

    
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),


    path('panel-superior/roles/', views.admin_superior_panel, name='gestionar_roles'),


    # Rutas para modificar sectores y puestos
    path('gestionar-pantallas/', views.lista_pantallas, name='lista_pantallas'),
    path('editar-pantalla/<int:pk>/', views.editar_pantalla, name='editar_pantalla'),
]