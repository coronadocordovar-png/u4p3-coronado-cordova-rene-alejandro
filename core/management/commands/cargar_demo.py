# date, timedelta: para poner fechas de factura en días distintos
from datetime import date, timedelta
# BaseCommand: la clase base de los comandos de "python manage.py ..." · CommandError: error que se muestra en la terminal
from django.core.management.base import BaseCommand, CommandError
# User: para buscar al usuario dueño de los datos
from django.contrib.auth.models import User
# transaction: todo o nada
from django.db import transaction
# los modelos que se llenan
from core.models import Categoria, Servicio, Factura, DetalleFactura

# CATEGORIAS: nombre y descripción; "Marketing" se queda sin servicios a propósito (aparece con 0 en la consulta 2)
CATEGORIAS = [
    # categoría 1
    ('Diseño', 'Logos, tarjetas e identidad visual'),
    # categoría 2
    ('Tutorías', 'Clases y asesorías académicas'),
    # categoría 3
    ('Desarrollo web', 'Sitios y aplicaciones'),
    # categoría 4: sin servicios
    ('Marketing', 'Campañas en redes sociales'),
# cierra la lista
]

# SERVICIOS: (título, precio, categoría); hay 2 empatados en el mínimo (150) y 2 en el máximo (2500)
SERVICIOS = [
    # empate en el precio MÍNIMO
    ('Clase de álgebra', '150.00', 'Tutorías'),
    # empate en el precio MÍNIMO
    ('Clase de física', '150.00', 'Tutorías'),
    # precio intermedio
    ('Tarjetas de presentación', '300.00', 'Diseño'),
    # precio intermedio
    ('Logo profesional', '800.00', 'Diseño'),
    # precio intermedio; nunca se vende (aparece en la consulta 4)
    ('Landing page', '1200.00', 'Desarrollo web'),
    # empate en el precio MÁXIMO
    ('Asesoría de tesis', '2500.00', 'Tutorías'),
    # empate en el precio MÁXIMO
    ('Sitio web completo', '2500.00', 'Desarrollo web'),
# cierra la lista
]

# FACTURAS: (cliente, días atrás, [(servicio, cantidad), ...])
FACTURAS = [
    # factura 1
    ('Papelería Luna', 20, [('Logo profesional', 1), ('Tarjetas de presentación', 2)]),
    # factura 2
    ('Colegio Ámbar', 15, [('Clase de álgebra', 4), ('Clase de física', 4)]),
    # factura 3
    ('Papelería Luna', 10, [('Tarjetas de presentación', 3)]),
    # factura 4
    ('Taller Ruiz', 7, [('Sitio web completo', 1)]),
    # factura 5
    ('Colegio Ámbar', 3, [('Asesoría de tesis', 1), ('Clase de álgebra', 2)]),
    # factura 6
    ('Ana Torres', 1, [('Clase de física', 2)]),
# cierra la lista
]


# Command: el nombre del archivo (cargar_demo.py) es el nombre del comando
class Command(BaseCommand):
    # help: texto que sale con "python manage.py help cargar_demo"
    help = 'Carga categorías, servicios y facturas de prueba para un usuario'

    # add_arguments: declara que el comando recibe el nombre de usuario
    def add_arguments(self, parser):
        # usuario: argumento obligatorio, ej. "python manage.py cargar_demo maria"
        parser.add_argument('usuario')

    # handle: lo que hace el comando
    def handle(self, *args, **opciones):
        # busca al usuario por su nombre
        try:
            # get: trae al usuario o lanza DoesNotExist
            usuario = User.objects.get(username=opciones['usuario'])
        # si no existe...
        except User.DoesNotExist:
            # ...se detiene con un mensaje claro
            raise CommandError('Ese usuario no existe. Escribe uno que ya tenga cuenta.')
        # atomic: si algo falla, no queda nada a medias
        with transaction.atomic():
            # recorre las categorías
            for nombre, descripcion in CATEGORIAS:
                # get_or_create: no la duplica si ya existe
                Categoria.objects.get_or_create(nombre=nombre, defaults={'descripcion': descripcion})
            # servicios: diccionario título → Servicio, para armar las facturas
            servicios = {}
            # recorre los servicios
            for titulo, precio, categoria in SERVICIOS:
                # get_or_create: busca por dueño y título; si no existe lo crea con estos datos
                servicio, creado = Servicio.objects.get_or_create(
                    # propietario: el usuario indicado
                    propietario=usuario,
                    # titulo: el título del servicio
                    titulo=titulo,
                    # defaults: solo se usan al crear
                    defaults={'descripcion': 'Servicio de prueba', 'precio': precio,
                              # categoria: la categoría por nombre
                              'categoria': Categoria.objects.get(nombre=categoria)},
                # cierra get_or_create
                )
                # guarda el servicio en el diccionario
                servicios[titulo] = servicio
            # si ya se habían cargado las facturas de prueba, no se repiten
            if Factura.objects.filter(usuario=usuario, cliente='Papelería Luna').exists():
                # aviso en amarillo
                self.stdout.write(self.style.WARNING('Las facturas de prueba ya existían; no se duplicaron.'))
                # termina el comando
                return
            # recorre las facturas
            for cliente, dias, renglones in FACTURAS:
                # crea el encabezado con la fecha de hace "dias" días
                factura = Factura.objects.create(usuario=usuario, cliente=cliente, fecha=date.today() - timedelta(days=dias))
                # recorre los renglones
                for titulo, cantidad in renglones:
                    # servicio del renglón
                    servicio = servicios[titulo]
                    # crea el renglón copiando el precio actual
                    DetalleFactura.objects.create(factura=factura, servicio=servicio, cantidad=cantidad, precio_unitario=servicio.precio)
        # mensaje verde de éxito
        self.stdout.write(self.style.SUCCESS(f'Datos de prueba cargados para {usuario.username}.'))