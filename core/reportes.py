# time: mide cuánto tarda MySQL en ejecutar una consulta
import time

# Decimal: permite reconocer los resultados monetarios
from decimal import Decimal

# connection: conexión de Django a MySQL
from django.db import connection


# CONSULTAS: los seis reportes SQL
# %(uid)s: identificador del usuario enviado de forma segura
CONSULTAS = [

    # Consulta 1: SUM() + GROUP BY
    {
        'clave': 'ingresos-por-categoria',
        'numero': 1,
        'titulo': 'Ingresos por categoría',
        'tecnica': 'SUM() + GROUP BY',
        'descripcion': 'Cuánto dinero ha generado cada categoría sumando todos los renglones de tus facturas.',
        'sql': """
-- Nombre de la categoría, unidades vendidas e ingresos
SELECT c.nombre AS categoria,
       SUM(d.cantidad) AS unidades_vendidas,
       SUM(d.cantidad * d.precio_unitario) AS ingresos
-- Se unen detalles, facturas, servicios y categorías
FROM core_detallefactura AS d
JOIN core_factura AS f ON f.id = d.factura_id
JOIN core_servicio AS s ON s.id = d.servicio_id
JOIN core_categoria AS c ON c.id = s.categoria_id
-- Solo facturas del usuario actual
WHERE f.usuario_id = %(uid)s
-- Agrupar por categoría
GROUP BY c.id, c.nombre
ORDER BY ingresos DESC
""",
    },

    # Consulta 2: COUNT() + GROUP BY + LEFT JOIN
    {
        'clave': 'servicios-por-categoria',
        'numero': 2,
        'titulo': 'Servicios por categoría',
        'tecnica': 'COUNT() + GROUP BY + LEFT JOIN',
        'descripcion': 'Cuántos servicios tienes en cada categoría, incluidas las categorías que todavía no usas (salen con 0).',
        'sql': """
-- Cuenta servicios por categoría
SELECT c.nombre AS categoria,
       COUNT(s.id) AS servicios
FROM core_categoria AS c
-- LEFT JOIN incluye categorías sin servicios
LEFT JOIN core_servicio AS s
       ON s.categoria_id = c.id
      AND s.propietario_id = %(uid)s
GROUP BY c.id, c.nombre
ORDER BY servicios DESC, c.nombre
""",
    },

    # Consulta 3: MIN() y MAX() con empates
    {
        'clave': 'precio-minimo-y-maximo',
        'numero': 3,
        'titulo': 'Servicio más barato y más caro (con empates)',
        'tecnica': 'MIN() + MAX() en una subconsulta',
        'descripcion': 'Muestra TODOS los servicios que tienen el precio mínimo y TODOS los que tienen el máximo: si dos cuestan lo mismo, salen los dos.',
        'sql': """
-- Clasifica cada servicio como más barato o más caro
SELECT CASE
           WHEN s.precio = m.minimo THEN 'Más barato (MIN)'
           ELSE 'Más caro (MAX)'
       END AS posicion,
       s.titulo AS servicio,
       c.nombre AS categoria,
       s.precio
FROM core_servicio AS s
-- Calcula los precios mínimo y máximo
JOIN (
    SELECT MIN(precio) AS minimo,
           MAX(precio) AS maximo
    FROM core_servicio
    WHERE propietario_id = %(uid)s
) AS m
    ON s.precio IN (m.minimo, m.maximo)
LEFT JOIN core_categoria AS c ON c.id = s.categoria_id
WHERE s.propietario_id = %(uid)s
ORDER BY s.precio, s.titulo
""",
    },

    # Consulta 4: LEFT JOIN + IS NULL
    {
        'clave': 'servicios-sin-vender',
        'numero': 4,
        'titulo': 'Servicios que nunca se han facturado',
        'tecnica': 'LEFT JOIN + IS NULL (anti-join)',
        'descripcion': 'Los servicios que todavía no aparecen en ninguna factura: candidatos a promoción o a revisar su precio.',
        'sql': """
-- Muestra los servicios sin detalles de factura
SELECT s.titulo AS servicio,
       c.nombre AS categoria,
       s.precio
FROM core_servicio AS s
LEFT JOIN core_detallefactura AS d
       ON d.servicio_id = s.id
LEFT JOIN core_categoria AS c
       ON c.id = s.categoria_id
WHERE s.propietario_id = %(uid)s
  AND d.id IS NULL
ORDER BY s.precio DESC
""",
    },

    # Consulta 5: HAVING + AVG()
    {
        'clave': 'clientes-sobre-el-promedio',
        'numero': 5,
        'titulo': 'Clientes que gastan más que el promedio',
        'tecnica': 'HAVING + subconsulta con AVG()',
        'descripcion': 'Tus mejores clientes: los que han comprado en total más que el promedio de todos tus clientes.',
        'sql': """
-- Total comprado por cliente
SELECT f.cliente,
       COUNT(DISTINCT f.id) AS facturas,
       SUM(d.cantidad * d.precio_unitario) AS total_comprado
FROM core_factura AS f
JOIN core_detallefactura AS d ON d.factura_id = f.id
WHERE f.usuario_id = %(uid)s
GROUP BY f.cliente
-- Conserva clientes que superan el promedio
HAVING SUM(d.cantidad * d.precio_unitario) > (
    SELECT AVG(t.total_cliente)
    FROM (
        SELECT SUM(d2.cantidad * d2.precio_unitario) AS total_cliente
        FROM core_factura AS f2
        JOIN core_detallefactura AS d2
             ON d2.factura_id = f2.id
        WHERE f2.usuario_id = %(uid)s
        GROUP BY f2.cliente
    ) AS t
)
ORDER BY total_comprado DESC
""",
    },

    # Consulta 6: WITH + RANK() OVER()
    {
        'clave': 'ranking-por-categoria',
        'numero': 6,
        'titulo': 'Ranking de servicios más vendidos por categoría',
        'tecnica': 'WITH (CTE) + RANK() OVER (PARTITION BY …)',
        'descripcion': 'El lugar de cada servicio dentro de su categoría según las unidades vendidas; si dos venden lo mismo, comparten el lugar.',
        'sql': """
-- CTE: calcula primero las ventas de cada servicio
WITH ventas AS (
    SELECT c.nombre AS categoria,
           s.titulo AS servicio,
           SUM(d.cantidad) AS unidades
    FROM core_detallefactura AS d
    JOIN core_factura AS f ON f.id = d.factura_id
    JOIN core_servicio AS s ON s.id = d.servicio_id
    JOIN core_categoria AS c ON c.id = s.categoria_id
    WHERE f.usuario_id = %(uid)s
    GROUP BY c.nombre, s.id, s.titulo
)
-- RANK asigna posiciones por categoría y conserva empates
SELECT categoria,
       RANK() OVER (
           PARTITION BY categoria
           ORDER BY unidades DESC
       ) AS lugar,
       servicio,
       unidades
FROM ventas
ORDER BY categoria, lugar, servicio
""",
    },

]


# Busca una consulta por su clave
def buscar(clave):
    for consulta in CONSULTAS:
        if consulta['clave'] == clave:
            return consulta
    return None


# Ejecuta SQL y devuelve columnas, filas y tiempo
def ejecutar_sql(sql, parametros=None):
    inicio = time.perf_counter()

    with connection.cursor() as cursor:
        cursor.execute(sql, parametros)
        columnas = [columna[0] for columna in cursor.description]
        filas = cursor.fetchall()

    milisegundos = (time.perf_counter() - inicio) * 1000
    return columnas, filas, milisegundos


# Convierte los resultados a texto para mostrarlos en tablas
def formatear(valor):
    if valor is None:
        return {'texto': '—', 'numero': False}

    if isinstance(valor, bool):
        return {'texto': 'Sí' if valor else 'No', 'numero': False}

    if isinstance(valor, int):
        return {'texto': f'{valor:,}', 'numero': True}

    if isinstance(valor, (Decimal, float)):
        return {'texto': f'{valor:,.2f}', 'numero': True}

    return {'texto': str(valor), 'numero': False}