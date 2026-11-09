# migrations: herramientas de Django para escribir migraciones a mano
from django.db import migrations


# copiar_categorias: función que Django ejecuta UNA vez cuando corres "migrate"
# apps: los modelos tal como estaban en ESTE punto de la historia (no importes desde core.models aquí)
# schema_editor: el objeto que habla con MySQL; esta función no lo necesita, pero Django siempre lo manda
def copiar_categorias(apps, schema_editor):
    # get_model: pide la versión "histórica" de Servicio, la que todavía tiene la columna de texto
    Servicio = apps.get_model('core', 'Servicio')
    # get_model: pide la versión histórica de Categoria, la tabla nueva del paso 01
    Categoria = apps.get_model('core', 'Categoria')
    # recorre todos los servicios de TODOS los usuarios, uno por uno
    for servicio in Servicio.objects.all():
        # strip(): quita espacios de más; si el texto quedó vacío se usa "Sin categoría"
        nombre = (servicio.categoria or '').strip() or 'Sin categoría'
        # nombre__iexact: busca la categoría sin importar mayúsculas ("diseño" y "Diseño" son la misma)
        categoria = Categoria.objects.filter(nombre__iexact=nombre).first()
        # si no existe todavía...
        if categoria is None:
            # ...la crea con el nombre tal como estaba escrito en el servicio
            categoria = Categoria.objects.create(nombre=nombre)
        # categoria_ref: apunta la llave foránea nueva a la categoría encontrada o creada
        servicio.categoria_ref = categoria
        # update_fields: guarda SOLO esa columna, sin tocar las demás
        servicio.save(update_fields=['categoria_ref'])


# class Migration: Django la generó con "makemigrations --empty"; solo cambias "operations"
class Migration(migrations.Migration):

    # dependencies: DÉJALA COMO LA ESCRIBIÓ DJANGO; apunta a tu migración anterior (su número puede ser otro)
    dependencies = [
        # ejemplo: la migración del paso 01; en tu archivo puede llamarse distinto
        ('core', '0002_categoria_servicio_categoria_ref'),
    # cierra la lista de dependencias
    ]

    # operations: lo que hace esta migración, en orden
    operations = [
        # RunPython: corre copiar_categorias al migrar; noop = si algún día deshaces la migración, no hace nada
        migrations.RunPython(copiar_categorias, migrations.RunPython.noop),
    # cierra la lista de operaciones
    ]