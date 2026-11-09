# forms: trae las herramientas de Django para construir formularios
from django import forms
# ValidationError: la excepción que Django usa para reportar un error de validación
from django.core.exceptions import ValidationError
# inlineformset_factory: fabrica un "formset" = varios formularios hijos (renglones) ligados a un padre (factura)
from django.forms import inlineformset_factory
# los modelos que usan estos formularios
from .models import Servicio, Categoria, Factura, DetalleFactura


# ServicioForm: el mismo ModelForm de la Semana 5; "categoria" ahora se dibuja como lista desplegable
class ServicioForm(forms.ModelForm):
    # Meta: de qué modelo sale el formulario y qué campos muestra
    class Meta:
        # model: el formulario se genera a partir del modelo Servicio
        model = Servicio
        # fields: los mismos 4 campos; como categoria ahora es llave foránea, Django pone un <select>
        fields = ['titulo', 'descripcion', 'precio', 'categoria']

    # clean_precio: tu validación de la Semana 5; no cambia
    def clean_precio(self):
        # self.cleaned_data: los valores ya convertidos a su tipo de Python
        precio = self.cleaned_data['precio']
        # regla propia: rechazar precios en cero o negativos
        if precio <= 0:
            # el formulario se vuelve inválido y muestra este mensaje junto al campo
            raise ValidationError('El precio debe ser mayor a 0.')
        # devuelve el valor limpio para que el formulario lo use
        return precio


# CategoriaForm: NUEVO formulario para dar de alta y editar categorías
class CategoriaForm(forms.ModelForm):
    # Meta: configuración del formulario
    class Meta:
        # model: sale del modelo Categoria
        model = Categoria
        # fields: los dos campos que se capturan
        fields = ['nombre', 'descripcion']
        # widgets: cambia cómo se dibuja un campo; aquí la descripción es una caja de 2 renglones
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 2})}


# FacturaForm: NUEVO formulario para el encabezado de la factura (cliente y fecha)
class FacturaForm(forms.ModelForm):
    # Meta: configuración del formulario
    class Meta:
        # model: sale del modelo Factura
        model = Factura
        # fields: usuario NO va aquí; lo pone la vista con request.user para que nadie lo falsifique
        fields = ['cliente', 'fecha']
        # widgets: type="date" muestra el calendario del navegador; format ISO para que el navegador lo entienda
        widgets = {'fecha': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')}


# DetalleFacturaForm: NUEVO formulario para UN renglón de la factura (servicio y cantidad)
class DetalleFacturaForm(forms.ModelForm):
    # Meta: configuración del formulario
    class Meta:
        # model: sale del modelo DetalleFactura
        model = DetalleFactura
        # fields: precio_unitario NO va aquí; la vista lo copia del servicio para que no se pueda alterar
        fields = ['servicio', 'cantidad']

    # __init__: se ejecuta al crear el formulario; recibe "usuario" para filtrar la lista de servicios
    def __init__(self, *args, usuario=None, **kwargs):
        # super().__init__: deja que Django arme el formulario normal primero
        super().__init__(*args, **kwargs)
        # queryset: en la lista desplegable solo aparecen TUS servicios; select_related evita una consulta por renglón
        self.fields['servicio'].queryset = Servicio.objects.filter(propietario=usuario).select_related('categoria')
        # label_from_instance: el texto de cada opción, con su precio (ej. "Clase de álgebra — $150.00")
        self.fields['servicio'].label_from_instance = lambda s: f'{s.titulo} — ${s.precio}'


# DetalleFormSet: varios DetalleFacturaForm juntos, todos ligados a UNA Factura
DetalleFormSet = inlineformset_factory(
    # Factura: el modelo padre
    Factura,
    # DetalleFactura: el modelo hijo (los renglones)
    DetalleFactura,
    # form: cada renglón usa el formulario de arriba
    form=DetalleFacturaForm,
    # extra=3: además del renglón obligatorio se dibujan 3 renglones vacíos
    extra=3,
    # min_num=1 + validate_min=True: la factura debe tener al menos 1 renglón lleno
    min_num=1,
    # validate_min: hace que el mínimo de arriba se revise al guardar
    validate_min=True,
    # can_delete=False: en una factura nueva no hace falta la casilla "borrar renglón"
    can_delete=False,
# cierra la llamada a inlineformset_factory
)