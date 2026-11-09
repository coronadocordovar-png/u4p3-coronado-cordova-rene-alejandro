from django.urls import path
from . import views
urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('servicios/', views.servicios, name='servicios'),
    path('servicios/nuevo/', views.servicio_nuevo, name='servicio_nuevo'),
    path('servicios/<int:pk>/editar/', views.servicio_editar, name='servicio_editar'),
    path('servicios/<int:pk>/eliminar/', views.servicio_eliminar, name='servicio_eliminar'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
]
