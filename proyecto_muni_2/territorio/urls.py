from django.urls import path
from . import views
urlpatterns = [
    path('catastro/', views.inicio_catastro, name='inicio_catastro'),
] # Lista vacía por ahora