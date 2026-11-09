# models: trae las herramientas de Django para describir tablas como clases
from django.db import models
# User: el modelo de usuario que Django ya trae incluido (login, contraseñas, sesiones)
from django.contrib.auth.models import User


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

    # __str__: el texto que representa al servicio; no cambia
    def __str__(self):
        # devuelve el título del servicio
        return self.titulo