# models: trae las herramientas de Django para describir tablas como clases
from django.db import models
# User: el modelo de usuario que Django ya trae incluido (login, contraseñas, sesiones)
from django.contrib.auth.models import User

# class Servicio: se convierte en la tabla "core_servicio" dentro de MySQL
class Categoria(models.Model):
    nombre = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.nombre

class Servicio(models.Model):
    # propietario: relaciona este servicio con el usuario dueño
    # on_delete=CASCADE: si se borra ese usuario, se borran también sus servicios
    propietario = models.ForeignKey(User, on_delete=models.CASCADE)

    # titulo: texto corto y obligatorio, máximo 120 caracteres
    titulo = models.CharField(max_length=120)

    # descripcion: texto largo, sin límite fijo de caracteres
    descripcion = models.TextField()

    # precio: número decimal — hasta 8 dígitos en total, 2 después del punto (ej. 1500.00)
    precio = models.DecimalField(max_digits=8, decimal_places=2)

    # categoria: texto corto para clasificar el servicio (ej. "Tutorías", "Diseño")


    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='servicios'
    )


    # creado_en: Django guarda automáticamente la fecha y hora cuando se crea el registro
    creado_en = models.DateTimeField(auto_now_add=True)

    # __str__: define qué texto se muestra al "imprimir" este objeto (ej. en el panel /admin)
    def __str__(self):
        # devuelve el título en vez de algo genérico como "Servicio object (1)"
        return self.titulo

class Factura(models.Model):
    propietario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='facturas'
    )
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,
        default='pendiente',
        db_index=True
    )

    def __str__(self):
        return f"Factura {self.pk}"



class DetalleFactura(models.Model):
    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.PROTECT,
        related_name='detalles_factura'
    )
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"Detalle {self.pk} - Factura {self.factura_id}"
