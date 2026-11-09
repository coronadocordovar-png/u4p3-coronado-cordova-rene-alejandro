# path: función para declarar cada ruta
from django.urls import path
# views: el archivo core/views.py
from . import views

# urlpatterns: la lista de rutas que Django revisa, en orden, para cada URL
urlpatterns = [
    # página de inicio (Semana 3)
    path('', views.inicio, name='inicio'),
    # listado de servicios
    path('servicios/', views.servicios, name='servicios'),
    # crear servicio
    path('servicios/nuevo/', views.crear_servicio, name='crear_servicio'),
    # editar servicio
    path('servicios/<int:pk>/editar/', views.editar_servicio, name='editar_servicio'),
    # eliminar servicio
    path('servicios/<int:pk>/eliminar/', views.eliminar_servicio, name='eliminar_servicio'),
    # NUEVA: lista y alta de categorías
    path('categorias/', views.categorias, name='categorias'),
    # NUEVA: editar una categoría
    path('categorias/<int:pk>/editar/', views.editar_categoria, name='editar_categoria'),
    # NUEVA: eliminar una categoría (solo POST)
    path('categorias/<int:pk>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),
    # NUEVA: lista de facturas
    path('facturas/', views.facturas, name='facturas'),
    # NUEVA: crear factura con sus renglones
    path('facturas/nueva/', views.crear_factura, name='crear_factura'),
    # NUEVA: detalle de una factura
    path('facturas/<int:pk>/', views.detalle_factura, name='detalle_factura'),
    # NUEVA: lista de reportes SQL
    path('reportes/', views.reportes, name='reportes'),
    # NUEVA: un reporte; <slug:clave> acepta letras, números y guiones (ej. ingresos-por-categoria)
    path('reportes/<slug:clave>/', views.reporte, name='reporte'),
    # registro (Semana 6)
    path('registro/', views.registro, name='registro'),
    # login (Semana 6)
    path('login/', views.iniciar_sesion, name='login'),
    # logout (Semana 6)
    path('logout/', views.cerrar_sesion, name='logout'),
# cierra la lista urlpatterns
]