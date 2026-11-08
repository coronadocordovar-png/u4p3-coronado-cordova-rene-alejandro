# U4P3 - Practica 1: Categorias, facturacion y reportes SQL

**Alumno:** Rene Alejandro Coronado Cordova
**Grupo:** DSM 4-1
**Carrera:** TSU en Desarrollo de Software Multiplataforma
**Institucion:** Universidad Tecnologica de Hermosillo
**Fecha:** 08/11/2026

## Descripcion del proyecto

Aplicacion web desarrollada con Django y MySQL para administrar
servicios, categorias y facturas, ademas de consultar seis reportes SQL.

El proyecto U4P3 continua el trabajo realizado en U4S8,
incorporando nuevas funcionalidades de administracion y consulta.

## Funcionalidades

- Registro, inicio y cierre de sesion.
- Administracion de servicios mediante CRUD.
- Busqueda de servicios y paginacion.
- Administracion de categorias.
- Creacion y consulta de facturas.
- Registro de detalles de factura.
- Calculo de importes de facturacion.
- Seis reportes SQL.
- Consulta del plan de ejecucion mediante EXPLAIN.
- Exportacion de resultados en formato CSV.

## Tecnologias

- Python
- Django 6.1.1
- MySQL en Aiven
- PyMySQL
- HTML y Tailwind CSS
- Git y GitHub
- Render
- Gunicorn
- WhiteNoise

## Repositorio

https://github.com/coronadocordovar-png/u4p3-practica1-coronado-cordova-rene-alejandro

## Aplicacion publicada

https://u4p3-practica1-coronado-cordova-rene.onrender.com

## Instalacion local

1. Clonar el repositorio.
2. Crear un entorno virtual de Python.
3. Instalar las dependencias:

   pip install -r requirements.txt

4. Configurar las variables de entorno tomando como referencia
   el archivo .env.example.

5. Configurar una base de datos MySQL autorizada.

6. Aplicar las migraciones:

   python manage.py migrate

7. Iniciar el servidor:

   python manage.py runserver

## Reportes SQL

El sistema incluye seis consultas SQL para analizar informacion
de servicios, categorias, facturas y clientes.

Los reportes permiten visualizar resultados y consultar el
plan de ejecucion mediante EXPLAIN.

## Evidencias

Consultar el archivo EVIDENCIAS.md y la carpeta evidencias/.

## Seguridad

Las credenciales y claves privadas se administran mediante
variables de entorno.

El archivo .env no debe publicarse ni incluirse en los
paquetes de entrega.

## Historial del proyecto

U4S8: version anterior del sistema de servicios.

U4P3: ampliacion con categorias, facturacion y reportes SQL.

## Verificacion

El proyecto dispone de evidencias de GitHub, Render,
categorias, servicios, facturas, resultados SQL y EXPLAIN.

Las pruebas deben realizarse utilizando una base de datos
de prueba y credenciales autorizadas.
