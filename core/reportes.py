# time: para medir cuántos milisegundos tarda MySQL en responder cada consulta
import time
# Decimal: el tipo de número que MySQL devuelve para precios y sumas de dinero
from decimal import Decimal
# connection: la misma conexión a MySQL que usa Django; con ella se ejecuta SQL escrito a mano
from django.db import connection


# CONSULTAS: la lista de reportes; cada uno es un diccionario con sus datos y su SQL escrito a mano
# %(uid)s: el lugar donde Django pondrá TU id de usuario de forma segura (nunca se pega texto dentro del SQL)
CONSULTAS = [
    # ---------- Consulta 1: SUM() + GROUP BY ----------
    {
        # clave: la parte final de la dirección, ej. /reportes/ingresos-por-categoria/
        'clave': 'ingresos-por-categoria',
        # numero: el número del reporte en la lista
        'numero': 1,
        # titulo: lo que se lee como encabezado
        'titulo': 'Ingresos por categoría',
        # tecnica: la técnica de SQL que practica esta consulta
        'tecnica': 'SUM() + GROUP BY',
        # descripcion: qué responde la consulta, en lenguaje de negocio
        'descripcion': 'Cuánto dinero ha generado cada categoría sumando todos los renglones de tus facturas.',
        # sql: la consulta escrita a mano; las líneas con -- son comentarios de SQL y MySQL las ignora
        'sql': """
-- columna 1: el nombre de la categoría
SELECT c.nombre AS categoria,
-- columna 2: SUM suma la cantidad de unidades vendidas de cada grupo
       SUM(d.cantidad) AS unidades_vendidas,
-- columna 3: SUM de cantidad por precio = el dinero cobrado en cada grupo
       SUM(d.cantidad * d.precio_unitario) AS ingresos
-- se parte de los renglones de factura (d)
FROM core_detallefactura AS d
-- cada renglón se une con su factura (f) para saber de quién es
JOIN core_factura AS f ON f.id = d.factura_id
-- y con su servicio (s) para llegar a la categoría
JOIN core_servicio AS s ON s.id = d.servicio_id
-- y con la categoría (c) para obtener su nombre
JOIN core_categoria AS c ON c.id = s.categoria_id
-- solo las facturas del usuario que tiene la sesión iniciada
WHERE f.usuario_id = %(uid)s
-- GROUP BY: junta en un solo renglón todo lo que sea de la misma categoría
GROUP BY c.id, c.nombre
-- ordena de la categoría que más vende a la que menos
ORDER BY ingresos DESC
-- fin del SQL: las comillas triples de abajo cierran el texto de la consulta
""",
    # cierra la consulta 1
    },
    # ---------- Consulta 2: COUNT() + GROUP BY ----------
    {
        # clave: parte final de la dirección
        'clave': 'servicios-por-categoria',
        # numero: número del reporte
        'numero': 2,
        # titulo: encabezado del reporte
        'titulo': 'Servicios por categoría',
        # tecnica: lo que se practica
        'tecnica': 'COUNT() + GROUP BY + LEFT JOIN',
        # descripcion: qué responde
        'descripcion': 'Cuántos servicios tienes en cada categoría, incluidas las categorías que todavía no usas (salen con 0).',
        # sql: la consulta escrita a mano
        'sql': """
-- columna 1: el nombre de la categoría
SELECT c.nombre AS categoria,
-- COUNT(s.id) cuenta solo los servicios que sí existen; COUNT(*) contaría 1 aunque no hubiera ninguno
       COUNT(s.id) AS servicios
-- se parte de TODAS las categorías
FROM core_categoria AS c
-- LEFT JOIN: conserva la categoría aunque no tenga servicios
LEFT JOIN core_servicio AS s
-- condición 1 de la unión: el servicio pertenece a esa categoría
       ON s.categoria_id = c.id
-- condición 2 (dentro del ON, no en WHERE): solo se cuentan TUS servicios
      AND s.propietario_id = %(uid)s
-- un renglón por categoría
GROUP BY c.id, c.nombre
-- primero las que tienen más servicios; si empatan, en orden alfabético
ORDER BY servicios DESC, c.nombre
-- fin del SQL: las comillas triples de abajo cierran el texto de la consulta
""",
    # cierra la consulta 2
    },
    # ---------- Consulta 3: MIN() y MAX() con empates ----------
    {
        # clave: parte final de la dirección
        'clave': 'precio-minimo-y-maximo',
        # numero: número del reporte
        'numero': 3,
        # titulo: encabezado del reporte
        'titulo': 'Servicio más barato y más caro (con empates)',
        # tecnica: lo que se practica
        'tecnica': 'MIN() + MAX() en una subconsulta',
        # descripcion: qué responde
        'descripcion': 'Muestra TODOS los servicios que tienen el precio mínimo y TODOS los que tienen el máximo: si dos cuestan lo mismo, salen los dos.',
        # sql: la consulta escrita a mano
        'sql': """
-- CASE: escribe una etiqueta según si el precio es el mínimo o el máximo
SELECT CASE WHEN s.precio = m.minimo THEN 'Más barato (MIN)' ELSE 'Más caro (MAX)' END AS posicion,
-- el título del servicio
       s.titulo AS servicio,
-- el nombre de su categoría
       c.nombre AS categoria,
-- su precio
       s.precio
-- se parte de los servicios (s)
FROM core_servicio AS s
-- subconsulta (m): calcula UNA sola vez el precio mínimo y el máximo de tus servicios
JOIN (SELECT MIN(precio) AS minimo, MAX(precio) AS maximo
-- de la tabla de servicios
      FROM core_servicio
-- solo los tuyos; el índice (propietario, precio) hace este paso muy rápido
      WHERE propietario_id = %(uid)s) AS m
-- IN: se queda con cada servicio cuyo precio sea igual al mínimo o al máximo (así entran los empates)
  ON s.precio IN (m.minimo, m.maximo)
-- LEFT JOIN: trae el nombre de la categoría (y no pierde el servicio si no tuviera)
LEFT JOIN core_categoria AS c ON c.id = s.categoria_id
-- otra vez solo tus servicios
WHERE s.propietario_id = %(uid)s
-- primero los baratos y luego los caros; los empates, por título
ORDER BY s.precio, s.titulo
-- fin del SQL: las comillas triples de abajo cierran el texto de la consulta
""",
    # cierra la consulta 3
    },
    # ---------- Consulta 4: servicios sin vender (LEFT JOIN + IS NULL) ----------
    {
        # clave: parte final de la dirección
        'clave': 'servicios-sin-vender',
        # numero: número del reporte
        'numero': 4,
        # titulo: encabezado del reporte
        'titulo': 'Servicios que nunca se han facturado',
        # tecnica: lo que se practica
        'tecnica': 'LEFT JOIN + IS NULL (anti-join)',
        # descripcion: qué responde
        'descripcion': 'Los servicios que todavía no aparecen en ninguna factura: candidatos a promoción o a revisar su precio.',
        # sql: la consulta escrita a mano
        'sql': """
-- columnas: título, categoría y precio del servicio
SELECT s.titulo AS servicio,
-- nombre de la categoría
       c.nombre AS categoria,
-- precio actual
       s.precio
-- se parte de los servicios (s)
FROM core_servicio AS s
-- LEFT JOIN con los renglones de factura: si el servicio nunca se vendió, d queda vacío (NULL)
LEFT JOIN core_detallefactura AS d ON d.servicio_id = s.id
-- trae el nombre de la categoría
LEFT JOIN core_categoria AS c ON c.id = s.categoria_id
-- solo tus servicios
WHERE s.propietario_id = %(uid)s
-- IS NULL: se queda SOLO con los que no encontraron ningún renglón de factura
  AND d.id IS NULL
-- los más caros primero
ORDER BY s.precio DESC
-- fin del SQL: las comillas triples de abajo cierran el texto de la consulta
""",
    # cierra la consulta 4
    },
    # ---------- Consulta 5: clientes por encima del promedio (HAVING) ----------
    {
        # clave: parte final de la dirección
        'clave': 'clientes-sobre-el-promedio',
        # numero: número del reporte
        'numero': 5,
        # titulo: encabezado del reporte
        'titulo': 'Clientes que gastan más que el promedio',
        # tecnica: lo que se practica
        'tecnica': 'HAVING + subconsulta con AVG()',
        # descripcion: qué responde
        'descripcion': 'Tus mejores clientes: los que han comprado en total más que el promedio de todos tus clientes.',
        # sql: la consulta escrita a mano
        'sql': """
-- columna 1: el nombre del cliente
SELECT f.cliente,
-- COUNT(DISTINCT f.id): cuántas facturas distintas tiene (DISTINCT evita contar una factura por cada renglón)
       COUNT(DISTINCT f.id) AS facturas,
-- SUM: el total que ha comprado
       SUM(d.cantidad * d.precio_unitario) AS total_comprado
-- se parte de las facturas (f)
FROM core_factura AS f
-- unidas con sus renglones (d)
JOIN core_detallefactura AS d ON d.factura_id = f.id
-- solo tus facturas
WHERE f.usuario_id = %(uid)s
-- un renglón por cliente
GROUP BY f.cliente
-- HAVING: filtra DESPUÉS de agrupar (WHERE no puede usar SUM); deja solo a quien supera el promedio
HAVING SUM(d.cantidad * d.precio_unitario) > (
-- AVG: el promedio de lo que compró cada cliente
    SELECT AVG(t.total_cliente)
-- t: una tabla temporal con el total de cada cliente
    FROM (SELECT SUM(d2.cantidad * d2.precio_unitario) AS total_cliente
-- facturas (f2) para la tabla temporal
          FROM core_factura AS f2
-- unidas con sus renglones (d2)
          JOIN core_detallefactura AS d2 ON d2.factura_id = f2.id
-- también solo las tuyas
          WHERE f2.usuario_id = %(uid)s
-- un total por cliente
          GROUP BY f2.cliente) AS t
-- cierra la subconsulta del promedio
)
-- el que más compra primero
ORDER BY total_comprado DESC
-- fin del SQL: las comillas triples de abajo cierran el texto de la consulta
""",
    # cierra la consulta 5
    },
    # ---------- Consulta 6: ranking con empates por categoría (RANK) ----------
    {
        # clave: parte final de la dirección
        'clave': 'ranking-por-categoria',
        # numero: número del reporte
        'numero': 6,
        # titulo: encabezado del reporte
        'titulo': 'Ranking de servicios más vendidos por categoría',
        # tecnica: lo que se practica
        'tecnica': 'WITH (CTE) + RANK() OVER (PARTITION BY …)',
        # descripcion: qué responde
        'descripcion': 'El lugar de cada servicio dentro de su categoría según las unidades vendidas; si dos venden lo mismo, comparten el lugar.',
        # sql: la consulta escrita a mano (MySQL 8 o más nuevo; Aiven usa MySQL 8)
        'sql': """
-- WITH: crea una tabla temporal llamada "ventas" que solo existe durante esta consulta
WITH ventas AS (
-- columna: nombre de la categoría
    SELECT c.nombre AS categoria,
-- columna: título del servicio
           s.titulo AS servicio,
-- columna: unidades vendidas de ese servicio
           SUM(d.cantidad) AS unidades
-- renglones de factura (d)
    FROM core_detallefactura AS d
-- con su factura (f)
    JOIN core_factura AS f ON f.id = d.factura_id
-- con su servicio (s)
    JOIN core_servicio AS s ON s.id = d.servicio_id
-- con su categoría (c)
    JOIN core_categoria AS c ON c.id = s.categoria_id
-- solo tus facturas
    WHERE f.usuario_id = %(uid)s
-- un renglón por servicio
    GROUP BY c.nombre, s.id, s.titulo
-- cierra la tabla temporal "ventas"
)
-- columna: la categoría
SELECT categoria,
-- RANK() OVER: numera 1, 2, 3… dentro de cada categoría (PARTITION BY); con empate repite el número
       RANK() OVER (PARTITION BY categoria ORDER BY unidades DESC) AS lugar,
-- columna: el servicio
       servicio,
-- columna: sus unidades
       unidades
-- se lee de la tabla temporal
FROM ventas
-- ordenado por categoría y luego por lugar
ORDER BY categoria, lugar, servicio
-- fin del SQL: las comillas triples de abajo cierran el texto de la consulta
""",
    # cierra la consulta 6
    },
# cierra la lista CONSULTAS
]


# buscar: devuelve la consulta cuya clave coincide, o None si no existe
def buscar(clave):
    # recorre la lista de consultas
    for consulta in CONSULTAS:
        # si la clave coincide con la que pidió la URL...
        if consulta['clave'] == clave:
            # ...devuelve ese diccionario
            return consulta
    # si ninguna coincidió, no hay reporte con esa clave
    return None


# ejecutar_sql: corre CUALQUIER consulta SELECT y devuelve columnas, filas y tiempo; no importa qué consulta sea
def ejecutar_sql(sql, parametros=None):
    # perf_counter: un cronómetro de alta precisión; se anota la hora de inicio
    inicio = time.perf_counter()
    # connection.cursor(): abre un cursor, el objeto que manda el SQL a MySQL y recibe la respuesta
    with connection.cursor() as cursor:
        # execute: manda el SQL; los parámetros se escapan por separado (protege contra inyección SQL)
        cursor.execute(sql, parametros)
        # description: los datos de cada columna del resultado; [0] es su nombre
        columnas = [columna[0] for columna in cursor.description]
        # fetchall: trae todas las filas del resultado como una lista de tuplas
        filas = cursor.fetchall()
    # milisegundos que pasaron desde el inicio
    milisegundos = (time.perf_counter() - inicio) * 1000
    # devuelve las tres cosas juntas
    return columnas, filas, milisegundos


# formatear: convierte un valor de MySQL en texto bonito y dice si es número (para alinearlo a la derecha)
def formatear(valor):
    # None: MySQL no tiene dato (NULL)
    if valor is None:
        # se muestra un guion largo
        return {'texto': '—', 'numero': False}
    # bool: verdadero/falso se muestra en español
    if isinstance(valor, bool):
        # Sí o No
        return {'texto': 'Sí' if valor else 'No', 'numero': False}
    # int: números enteros con separador de miles (1,250)
    if isinstance(valor, int):
        # :, agrega las comas de miles
        return {'texto': f'{valor:,}', 'numero': True}
    # Decimal o float: dinero y promedios con 2 decimales (1,250.50)
    if isinstance(valor, (Decimal, float)):
        # :,.2f = comas de miles y 2 decimales
        return {'texto': f'{valor:,.2f}', 'numero': True}
    # cualquier otra cosa (texto, fechas): se convierte a texto tal cual
    return {'texto': str(valor), 'numero': False}