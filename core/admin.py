# admin: el panel de administración que Django trae de fábrica (/admin)
from django.contrib import admin
# los 4 modelos de la app: el que ya tenías y los 3 nuevos
from .models import Servicio, Categoria, Factura, DetalleFactura


# register(Servicio): igual que desde la Semana 4; ahora con columnas visibles en la lista
@admin.register(Servicio)
# ServicioAdmin: configura cómo se ve Servicio dentro de /admin
class ServicioAdmin(admin.ModelAdmin):
    # list_display: columnas que se ven en la lista de servicios
    list_display = ['titulo', 'categoria', 'precio', 'propietario']
    # list_filter: filtros de la barra derecha (por categoría)
    list_filter = ['categoria']


# register(Categoria): la tabla nueva aparece en /admin
@admin.register(Categoria)
# CategoriaAdmin: configuración de Categoria en /admin
class CategoriaAdmin(admin.ModelAdmin):
    # list_display: columnas visibles
    list_display = ['nombre', 'descripcion']


# DetalleFacturaInline: muestra los renglones DENTRO de la pantalla de cada factura
class DetalleFacturaInline(admin.TabularInline):
    # model: los renglones son registros de DetalleFactura
    model = DetalleFactura
    # extra: cuántos renglones vacíos extra se muestran para capturar
    extra = 1


# register(Factura): la tabla nueva aparece en /admin, con sus renglones incluidos
@admin.register(Factura)
# FacturaAdmin: configuración de Factura en /admin
class FacturaAdmin(admin.ModelAdmin):
    # list_display: folio es la @property del modelo; también se puede mostrar como columna
    list_display = ['folio', 'cliente', 'fecha', 'usuario']
    # inlines: dibuja la tabla de renglones debajo de los datos de la factura
    inlines = [DetalleFacturaInline]