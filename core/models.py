from django.db import models
from django.contrib.auth.models import User

# Modelo inicial de Unidad 2: categoría todavía es texto.
# El paso 02 de la guía agrega la tabla Categoria y una relación temporal.
class Servicio(models.Model):
    propietario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=120)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    categoria = models.CharField(max_length=60)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
