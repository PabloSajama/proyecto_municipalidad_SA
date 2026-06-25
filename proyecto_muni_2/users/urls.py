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

     # Ruta para Perfil de usuario
     path('perfil/', views.ver_perfil_view, name='ver_perfil'),
     path('perfil/editar/', views.editar_perfil_view, name='editar_perfil'),

    # --- CIRCUITO OPTIMIZADO DE RECUPERACIÓN DE CONTRASEÑA ---
    # 1. Formulario para ingresar el Email
    path('olvide-password/', 
         views.OlvidePasswordView.as_view(), 
         name='password_reset'),
    # 2. Confirmación de correo enviado
    path('olvide-password/enviado/', 
         views.OlvidePasswordDoneView.as_view(), 
         name='password_reset_done'),
    # 3. Link seguro del mail para meter la nueva contraseña (vuelve directo al login)
    path('olvide-password/restablecer/<uidb64>/<token>/', 
         views.OlvidePasswordConfirmView.as_view(), 
         name='password_reset_confirm'),
]