from django.urls import path # type: ignore
from app1 import views

urlpatterns = [
    path('', views.bienvenida, name='bienvenida'),
    path('login/', views.login, name='login'),
    path('registro/', views.registro, name='registro'),
    path('entrada/', views.entrada, name='entrada'),
    path('contactos/', views.contactos, name='contactos'),
    path('servicios/', views.servicios, name='servicios'),
    path('informacion/', views.informacion, name='informacion'),
    
]