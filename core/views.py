# csv: para armar el archivo .csv que se descarga desde cada reporte
import csv
# render, redirect, get_object_or_404: los mismos atajos de Django que ya usabas
from django.shortcuts import render, redirect, get_object_or_404
# HttpResponse: respuesta "a mano" (la usa la descarga CSV) · Http404: error "no existe"
from django.http import HttpResponse, Http404
# connection: datos de la conexión (vista inicio) · transaction: guardar todo o nada · DatabaseError: errores de MySQL
from django.db import connection, transaction, DatabaseError
# Sum, Count, F, Q: funciones del ORM para sumar, contar, usar columnas y combinar filtros · ProtectedError: aviso de PROTECT
from django.db.models import Sum, Count, F, Q, ProtectedError
# login_required: decorador que exige sesión iniciada
from django.contrib.auth.decorators import login_required
# login: inicia la sesión de un usuario · logout: la cierra
from django.contrib.auth import login, logout
# UserCreationForm: registro listo · AuthenticationForm: inicio de sesión listo
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# messages: mensajes flash que se muestran una sola vez
from django.contrib import messages
# Paginator: divide una lista larga en páginas
from django.core.paginator import Paginator
# los 3 modelos que usan estas vistas (DetalleFactura se usa a través de factura.detalles)
from .models import Servicio, Categoria, Factura
# los formularios: el de servicio que ya tenías y los 3 nuevos
from .forms import ServicioForm, CategoriaForm, FacturaForm, DetalleFormSet
# reportes: el archivo nuevo con las consultas SQL escritas a mano
from . import reportes as reportes_sql


# inicio: la vista de la Semana 3 que muestra a qué base estás conectado (no cambia)
def inicio(request):
    # settings_dict: diccionario con ENGINE, HOST, NAME, etc. de la conexión activa
    info_bd = connection.settings_dict
    # contexto: los datos que la plantilla podrá usar
    contexto = {
        # motor: el tipo de base de datos (debe decir mysql)
        'motor': info_bd['ENGINE'],
        # host: el servidor de la base (en Aiven termina en aivencloud.com)
        'host': info_bd['HOST'],
    # cierre del diccionario contexto
    }
    # render: junta inicio.html con el contexto y devuelve la página
    return render(request, 'core/inicio.html', contexto)


# @login_required: si no hay sesión, manda a LOGIN_URL
@login_required
# servicios: el listado de la Semana 7, ahora también busca por categoría y trae la categoría en la misma consulta
def servicios(request):
    # select_related('categoria'): un JOIN trae servicio + categoría de una vez (sin esto, 1 consulta extra por renglón)
    lista_servicios = Servicio.objects.filter(propietario=request.user).select_related('categoria').order_by('-creado_en', '-id')
    # q: el texto del buscador; '' si no hay búsqueda
    query = request.GET.get('q', '').strip()
    # si el usuario escribió algo...
    if query:
        # Q(...) | Q(...): busca el texto en el título O en el nombre de la categoría
        lista_servicios = lista_servicios.filter(Q(titulo__icontains=query) | Q(categoria__nombre__icontains=query))
    # Paginator: páginas de 5 registros
    paginator = Paginator(lista_servicios, 5)
    # get_page: la página pedida en ?page=
    pagina = paginator.get_page(request.GET.get('page'))
    # render: la misma plantilla de la Semana 7 (con la columna Categoría nueva)
    return render(request, 'core/servicios.html', {'servicios': pagina, 'query': query})


# @login_required: solo con sesión
@login_required
# crear_servicio: no cambia respecto a la Semana 7
def crear_servicio(request):
    # POST = el usuario envió el formulario
    if request.method == 'POST':
        # reconstruye el formulario con lo que tecleó
        form = ServicioForm(request.POST)
        # valida tipos, obligatorios y clean_precio
        if form.is_valid():
            # crea el objeto en memoria sin guardarlo todavía
            nuevo = form.save(commit=False)
            # el dueño lo pone la vista, no el formulario
            nuevo.propietario = request.user
            # ahora sí lo guarda en MySQL
            nuevo.save()
            # regresa al listado
            return redirect('servicios')
    # GET = el usuario apenas abrió la página
    else:
        # formulario vacío
        form = ServicioForm()
    # dibuja el formulario (vacío o con errores)
    return render(request, 'core/servicio_form.html', {'form': form, 'titulo_pagina': 'Nuevo servicio'})


# @login_required: solo con sesión
@login_required
# editar_servicio: no cambia respecto a la Semana 7
def editar_servicio(request, pk):
    # el id correcto Y que sea tuyo; si no, 404
    servicio = get_object_or_404(Servicio, pk=pk, propietario=request.user)
    # POST = se enviaron cambios
    if request.method == 'POST':
        # instance: actualiza ESE registro
        form = ServicioForm(request.POST, instance=servicio)
        # valida los datos
        if form.is_valid():
            # guarda el UPDATE en MySQL
            form.save()
            # regresa al listado
            return redirect('servicios')
    # GET = se abrió la pantalla de edición
    else:
        # formulario precargado
        form = ServicioForm(instance=servicio)
    # dibuja el mismo template de crear
    return render(request, 'core/servicio_form.html', {'form': form, 'titulo_pagina': 'Editar servicio'})


# @login_required: solo con sesión
@login_required
# eliminar_servicio: CAMBIA; si el servicio ya está en una factura, PROTECT impide borrarlo y se avisa
def eliminar_servicio(request, pk):
    # el id correcto Y que sea tuyo; si no, 404
    servicio = get_object_or_404(Servicio, pk=pk, propietario=request.user)
    # solo se borra con el botón de confirmar (POST)
    if request.method == 'POST':
        # try: intenta borrar
        try:
            # delete(): borra la fila en MySQL
            servicio.delete()
            # mensaje verde de confirmación
            messages.success(request, f'Se eliminó "{servicio.titulo}".')
        # ProtectedError: Django lo lanza porque DetalleFactura.servicio tiene on_delete=PROTECT
        except ProtectedError:
            # messages.error: mensaje rojo; el servicio sigue existiendo
            messages.error(request, f'No se puede eliminar "{servicio.titulo}": ya aparece en una factura.')
        # en ambos casos regresa al listado
        return redirect('servicios')
    # GET: solo muestra la pantalla de "¿Seguro?"
    return render(request, 'core/servicio_confirm_delete.html', {'servicio': servicio})


# @login_required: solo con sesión
@login_required
# categorias: NUEVA; en la misma página se listan las categorías y se da de alta una nueva
def categorias(request):
    # POST = se envió el formulario de "Nueva categoría"
    if request.method == 'POST':
        # reconstruye el formulario con lo tecleado
        form = CategoriaForm(request.POST)
        # valida (incluye que el nombre no se repita, por unique=True)
        if form.is_valid():
            # guarda la categoría en MySQL
            form.save()
            # mensaje verde
            messages.success(request, 'Categoría creada.')
            # recarga la misma página (evita reenvíos al recargar)
            return redirect('categorias')
    # GET = se abrió la página
    else:
        # formulario vacío
        form = CategoriaForm()
    # annotate + Count: agrega a cada categoría cuántos servicios TUYOS tiene, en una sola consulta (GROUP BY)
    lista = Categoria.objects.annotate(total_servicios=Count('servicios', filter=Q(servicios__propietario=request.user)))
    # dibuja la página con el formulario y la lista
    return render(request, 'core/categorias.html', {'form': form, 'categorias': lista})


# @login_required: solo con sesión
@login_required
# editar_categoria: NUEVA; cambia el nombre o la descripción de una categoría
def editar_categoria(request, pk):
    # busca la categoría; si no existe, 404 (las categorías son un catálogo común para todos)
    categoria = get_object_or_404(Categoria, pk=pk)
    # POST = se enviaron cambios
    if request.method == 'POST':
        # instance: actualiza ESA categoría
        form = CategoriaForm(request.POST, instance=categoria)
        # valida
        if form.is_valid():
            # guarda el UPDATE
            form.save()
            # mensaje verde
            messages.success(request, 'Categoría actualizada.')
            # regresa a la lista
            return redirect('categorias')
    # GET = se abrió la pantalla
    else:
        # formulario precargado
        form = CategoriaForm(instance=categoria)
    # dibuja el formulario de edición
    return render(request, 'core/categoria_form.html', {'form': form})


# @login_required: solo con sesión
@login_required
# eliminar_categoria: NUEVA; solo acepta POST y respeta PROTECT
def eliminar_categoria(request, pk):
    # busca la categoría o da 404
    categoria = get_object_or_404(Categoria, pk=pk)
    # solo se borra con el botón (POST), nunca con un enlace (GET)
    if request.method == 'POST':
        # try: intenta borrar
        try:
            # delete(): borra la fila
            categoria.delete()
            # mensaje verde
            messages.success(request, f'Se eliminó la categoría "{categoria.nombre}".')
        # ProtectedError: la categoría todavía tiene servicios (Servicio.categoria es PROTECT)
        except ProtectedError:
            # mensaje rojo
            messages.error(request, f'No se puede eliminar "{categoria.nombre}": todavía tiene servicios.')
    # en cualquier caso regresa a la lista
    return redirect('categorias')


# @login_required: solo con sesión
@login_required
# facturas: NUEVA; lista tus facturas con su total calculado por MySQL
def facturas(request):
    # annotate: MySQL calcula para cada factura su total (SUM) y cuántos renglones tiene (COUNT) en UNA consulta
    lista = (Factura.objects.filter(usuario=request.user)
             # total: suma de cantidad × precio_unitario de sus renglones
             .annotate(total=Sum(F('detalles__cantidad') * F('detalles__precio_unitario')),
                       # partidas: número de renglones
                       partidas=Count('detalles'))
             # order_by: con annotate (GROUP BY) Django ignora el ordering del Meta; se repite aquí para paginar bien
             .order_by('-fecha', '-id'))
    # Paginator: páginas de 10 facturas
    pagina = Paginator(lista, 10).get_page(request.GET.get('page'))
    # dibuja la lista
    return render(request, 'core/facturas.html', {'facturas': pagina})


# @login_required: solo con sesión
@login_required
# crear_factura: NUEVA; guarda el encabezado y sus renglones juntos
def crear_factura(request):
    # factura nueva en memoria, ya con el usuario que la emite
    factura = Factura(usuario=request.user)
    # POST = se envió el formulario
    if request.method == 'POST':
        # form: el encabezado (cliente y fecha)
        form = FacturaForm(request.POST, instance=factura)
        # formset: los renglones; form_kwargs manda el usuario a cada DetalleFacturaForm para filtrar sus servicios
        formset = DetalleFormSet(request.POST, instance=factura, form_kwargs={'usuario': request.user})
        # ambos deben ser válidos: datos del encabezado y al menos 1 renglón correcto
        if form.is_valid() and formset.is_valid():
            # transaction.atomic: si algo falla a la mitad, MySQL deshace TODO (no quedan facturas sin renglones)
            with transaction.atomic():
                # guarda el encabezado; ahora la factura ya tiene id
                factura = form.save()
                # commit=False: arma los renglones sin guardarlos para completarles el precio
                detalles = formset.save(commit=False)
                # recorre cada renglón capturado
                for detalle in detalles:
                    # precio_unitario: se copia del servicio en este momento (precio histórico)
                    detalle.precio_unitario = detalle.servicio.precio
                    # guarda el renglón ligado a la factura
                    detalle.save()
            # mensaje verde con el folio
            messages.success(request, f'Factura {factura.folio} guardada.')
            # va al detalle de la factura recién creada
            return redirect('detalle_factura', pk=factura.pk)
    # GET = se abrió la página
    else:
        # encabezado vacío
        form = FacturaForm(instance=factura)
        # renglones vacíos, con la lista de servicios filtrada al usuario
        formset = DetalleFormSet(instance=factura, form_kwargs={'usuario': request.user})
    # dibuja el formulario
    return render(request, 'core/factura_form.html', {'form': form, 'formset': formset})


# @login_required: solo con sesión
@login_required
# detalle_factura: NUEVA; muestra una factura con sus renglones y su total
def detalle_factura(request, pk):
    # el id correcto Y que la hayas emitido tú; si no, 404
    factura = get_object_or_404(Factura, pk=pk, usuario=request.user)
    # select_related: trae servicio y categoría de cada renglón en la misma consulta
    detalles = factura.detalles.select_related('servicio__categoria')
    # aggregate: MySQL suma el total de la factura; "or 0" por si no tuviera renglones
    total = detalles.aggregate(total=Sum(F('cantidad') * F('precio_unitario')))['total'] or 0
    # dibuja el detalle
    return render(request, 'core/factura_detalle.html', {'factura': factura, 'detalles': detalles, 'total': total})


# @login_required: solo con sesión
@login_required
# reportes: NUEVA; la lista de los 6 reportes con SQL escrito a mano
def reportes(request):
    # manda la lista CONSULTAS de reportes.py a la plantilla
    return render(request, 'core/reportes.html', {'consultas': reportes_sql.CONSULTAS})


# @login_required: solo con sesión
@login_required
# reporte: NUEVA; ejecuta UNA consulta y la dibuja como tabla, sin importar cuál sea
def reporte(request, clave):
    # buscar: encuentra la consulta por su clave (la parte final de la URL)
    consulta = reportes_sql.buscar(clave)
    # si no existe esa clave...
    if consulta is None:
        # ...error 404
        raise Http404('Reporte no encontrado')
    # parametros: el valor de %(uid)s; Django lo pasa a MySQL de forma segura
    parametros = {'uid': request.user.id}
    # ver_plan: True si la URL trae ?plan=1 (botón "Ver plan EXPLAIN")
    ver_plan = request.GET.get('plan') == '1'
    # EXPLAIN + la consulta: MySQL no ejecuta la consulta, explica CÓMO la ejecutaría (qué índices usa)
    sql = 'EXPLAIN ' + consulta['sql'] if ver_plan else consulta['sql']
    # error: aquí se guarda el mensaje si MySQL rechaza el SQL
    error = None
    # try: intenta ejecutar el SQL
    try:
        # ejecutar_sql: devuelve nombres de columnas, filas y milisegundos
        columnas, filas, milisegundos = reportes_sql.ejecutar_sql(sql, parametros)
    # DatabaseError: un error de SQL (columna mal escrita, coma de más, etc.)
    except DatabaseError as e:
        # se muestra en la página en vez de tumbar el sitio con un error 500
        columnas, filas, milisegundos, error = [], [], 0, str(e)
    # ?formato=csv: descarga del resultado
    if request.GET.get('formato') == 'csv' and error is None:
        # content_type: le dice al navegador que es un archivo CSV en UTF-8
        respuesta = HttpResponse(content_type='text/csv; charset=utf-8')
        # Content-Disposition: lo descarga con el nombre de la clave (ej. ingresos-por-categoria.csv)
        respuesta['Content-Disposition'] = f'attachment; filename="{clave}.csv"'
        # '﻿': marca invisible para que Excel lea bien los acentos
        respuesta.write('﻿')
        # csv.writer: escribe renglones separados por comas en la respuesta
        escritor = csv.writer(respuesta)
        # primer renglón: los nombres de las columnas
        escritor.writerow(columnas)
        # después, cada fila del resultado
        escritor.writerows(filas)
        # entrega el archivo
        return respuesta
    # celdas: cada valor convertido a {'texto', 'numero'} para dibujarlo bonito y alinear los números
    celdas = [[reportes_sql.formatear(valor) for valor in fila] for fila in filas]
    # contexto: todo lo que la plantilla necesita
    contexto = {
        # consulta: título, técnica, descripción y SQL
        'consulta': consulta,
        # sql_mostrado: el SQL que realmente se ejecutó (con EXPLAIN si se pidió)
        'sql_mostrado': sql.strip(),
        # columnas: encabezados de la tabla
        'columnas': columnas,
        # filas: las celdas ya formateadas
        'filas': celdas,
        # milisegundos: redondeado a 1 decimal
        'milisegundos': round(milisegundos, 1),
        # ver_plan: para marcar qué botón está activo
        'ver_plan': ver_plan,
        # error: el mensaje de MySQL o None
        'error': error,
    # cierra el contexto
    }
    # dibuja la página del reporte
    return render(request, 'core/reporte.html', contexto)


# registro: no cambia (Semana 6)
def registro(request):
    # POST = se envió el formulario de registro
    if request.method == 'POST':
        # reconstruye el formulario
        form = UserCreationForm(request.POST)
        # valida usuario y contraseñas
        if form.is_valid():
            # crea el usuario con la contraseña hasheada
            usuario_nuevo = form.save()
            # inicia sesión automáticamente
            login(request, usuario_nuevo)
            # mensaje de bienvenida
            messages.success(request, f'Cuenta creada. ¡Bienvenido, {usuario_nuevo.username}!')
            # va al listado
            return redirect('servicios')
    # GET = se abrió la página
    else:
        # formulario vacío
        form = UserCreationForm()
    # dibuja el registro
    return render(request, 'core/registro.html', {'form': form})


# iniciar_sesion: no cambia (Semana 6)
def iniciar_sesion(request):
    # POST = se enviaron usuario y contraseña
    if request.method == 'POST':
        # el formulario de login necesita request
        form = AuthenticationForm(request, data=request.POST)
        # valida contra la base
        if form.is_valid():
            # guarda la sesión
            login(request, form.get_user())
            # mensaje verde
            messages.success(request, 'Sesión iniciada correctamente.')
            # va al listado
            return redirect('servicios')
    # GET = se abrió la página
    else:
        # formulario vacío
        form = AuthenticationForm()
    # dibuja el login
    return render(request, 'core/login.html', {'form': form})


# cerrar_sesion: no cambia (Semana 6)
def cerrar_sesion(request):
    # invalida la sesión
    logout(request)
    # mensaje informativo
    messages.info(request, 'Sesión cerrada correctamente.')
    # va al login
    return redirect('login')