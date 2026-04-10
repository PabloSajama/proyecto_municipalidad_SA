from django.urls import path
from . import views
urlpatterns = [

    path('rentas/', views.inicio_rentas, name='inicio_rentas'),
    path('rentas/automotor/', views.automotor, name='automotor'),
    path('rentas/licencia-conducir/', views.licencia_conducir, name='licencia_conducir'),
    path('rentas/impuesto-inmobiliario/', views.impuesto_inmobiliario, name='impuesto_inmobiliario'),
    path('rentas/habilitaciones-negocio/', views.habilitaciones_negocio, name='habilitaciones_negocio'),
    path('rentas/alumbrado-limpieza/', views.alumbrado_limpieza, name='alumbrado_limpieza'),


    ## url para licencia de conducir, impuesto inmobiliario, habilitaciones de negocio y alumbrado y limpieza
    path('licencia/', views.inicio_licencia, name='inicio_licencia'),
] # Lista vacía por ahora