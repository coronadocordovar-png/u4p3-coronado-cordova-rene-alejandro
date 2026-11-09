# models: trae las herramientas de Django para describir tablas como clases
from django.db import models
# User: el modelo de usuario que Django ya trae incluido (login, contraseñas, sesiones)
from django.contrib.auth.models import User
# timezone: da la fecha de hoy según la zona horaria de settings.py
from django.utils import timezone


# class Categoria: NUEVA tabla "core_categoria"; va ARRIBA de Servicio porque Servicio la va a usar
class Categoria(models.Model):
    # nombre: texto corto y obligatorio; unique=True impide dos categorías con el mismo nombre
    nombre = models.CharField(max_length=60, unique=True)

    # descripcion: texto largo opcional; blank=True permite dejarlo vacío en los formularios
    descripcion = models.TextField(blank=True)

    # class Meta: opciones extra de la tabla (no son columnas)
    class Meta:
        # ordering: cuando se pidan categorías, saldrán ordenadas por nombre de la A a la Z
        ordering = ['nombre']

    # __str__: el texto que se ve en las listas desplegables y en /admin
    def __str__(self):
        # devuelve el nombre en vez de "Categoria object (1)"
        return self.nombre


# class Servicio: la tabla "core_servicio" que ya tienes desde la Unidad 2
class Servicio(models.Model):
    # propietario: el usuario dueño del servicio (Semana 6); no cambia
    propietario = models.ForeignKey(User, on_delete=models.CASCADE)

    # titulo: texto corto y obligatorio; no cambia
    titulo = models.CharField(max_length=120)

    # descripcion: texto largo; no cambia
    descripcion = models.TextField()

    # precio: decimal con 2 dígitos después del punto; no cambia
    precio = models.DecimalField(max_digits=8, decimal_places=2)

    # categoria: AHORA es llave foránea a Categoria (antes era texto); en MySQL la columna se llama categoria_id
    # on_delete=PROTECT: MySQL no deja borrar una categoría si todavía tiene servicios
    # null=True: la columna acepta vacío, pero el formulario sí la exige (no tiene blank=True)
    # related_name='servicios': desde una categoría se llega a sus servicios con categoria.servicios
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, null=True, related_name='servicios')

    # creado_en: fecha y hora de creación automática; no cambia
    creado_en = models.DateTimeField(auto_now_add=True)

    # class Meta: NUEVA en Servicio; aquí van los índices para que las consultas sean rápidas
    class Meta:
        # indexes: lista de índices que Django creará en MySQL con "migrate"
        indexes = [
            # índice compuesto (propietario, precio): acelera "los servicios de un usuario" y su MIN/MAX de precio
            models.Index(fields=['propietario', 'precio'], name='servicio_prop_precio_idx'),
        # cierra la lista de índices
        ]

    # __str__: el texto que representa al servicio; no cambia
    def __str__(self):
        # devuelve el título del servicio
        return self.titulo


# class Factura: NUEVA tabla "core_factura"; el encabezado de cada venta
class Factura(models.Model):
    # usuario: quién emite la factura (el dueño de los servicios); el mismo candado que propietario en Servicio
    # related_name='facturas': desde un usuario se llega a sus facturas con usuario.facturas
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='facturas')

    # cliente: nombre de la persona o empresa a la que le vendes
    cliente = models.CharField(max_length=120)

    # fecha: día de la venta; default=timezone.localdate pone la fecha de hoy si no se escribe otra
    fecha = models.DateField(default=timezone.localdate)

    # creado_en: fecha y hora exacta en que se guardó el registro
    creado_en = models.DateTimeField(auto_now_add=True)

    # class Meta: orden por defecto e índices de la tabla
    class Meta:
        # ordering: primero las facturas más recientes; '-id' desempata las del mismo día
        ordering = ['-fecha', '-id']
        # indexes: lista de índices de esta tabla
        indexes = [
            # índice compuesto (usuario, fecha): acelera "mis facturas" y los reportes por fecha
            models.Index(fields=['usuario', 'fecha'], name='factura_usuario_fecha_idx'),
        # cierra la lista de índices
        ]

    # @property: folio se usa como si fuera un campo (factura.folio), pero se calcula y no ocupa columna
    @property
    # folio: arma un folio legible a partir del id
    def folio(self):
        # si la factura todavía no se guarda, no tiene id
        if self.pk is None:
            # texto provisional mientras no exista en MySQL
            return 'F-nueva'
        # :05d rellena con ceros a la izquierda: id 7 → F-00007
        return f'F-{self.pk:05d}'

    # __str__: texto que representa a la factura en /admin
    def __str__(self):
        # ejemplo: "F-00007 · Papelería Luna"
        return f'{self.folio} · {self.cliente}'


# class DetalleFactura: NUEVA tabla "core_detallefactura"; cada renglón (partida) de una factura
class DetalleFactura(models.Model):
    # factura: a qué factura pertenece el renglón; CASCADE = si se borra la factura, se borran sus renglones
    # related_name='detalles': desde una factura se llega a sus renglones con factura.detalles
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='detalles')

    # servicio: qué servicio se vendió; PROTECT = no se puede borrar un servicio que ya aparece en una factura
    # related_name='detalles': desde un servicio se llega a los renglones donde se vendió
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT, related_name='detalles')

    # cantidad: cuántas unidades se vendieron; solo números enteros positivos, 1 si no se indica
    cantidad = models.PositiveIntegerField(default=1)

    # precio_unitario: el precio AL MOMENTO de la venta; si mañana cambias el precio, la factura no cambia
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    # @property: subtotal se calcula, no se guarda en MySQL
    @property
    # subtotal: cantidad por precio unitario
    def subtotal(self):
        # ejemplo: 3 × 150.00 = 450.00
        return self.cantidad * self.precio_unitario

    # __str__: texto que representa al renglón en /admin
    def __str__(self):
        # ejemplo: "3 × Clase de álgebra"
        return f'{self.cantidad} × {self.servicio}'