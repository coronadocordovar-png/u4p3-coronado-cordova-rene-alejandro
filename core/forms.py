from django import forms
from django.core.exceptions import ValidationError
from .models import Servicio

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['titulo', 'descripcion', 'precio', 'categoria']

    def clean_precio(self):
        precio = self.cleaned_data['precio']
        if precio <= 0:
            raise ValidationError('El precio debe ser mayor a 0.')
        return precio
