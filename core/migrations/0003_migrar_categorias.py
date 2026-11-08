from django.db import migrations


def migrar_categorias(apps, schema_editor):
    Categoria = apps.get_model('core', 'Categoria')
    Servicio = apps.get_model('core', 'Servicio')
    db = schema_editor.connection.alias

    for servicio in Servicio.objects.using(db).all():
        nombre = servicio.categoria.strip()

        if nombre:
            categoria, creada = Categoria.objects.using(db).get_or_create(
                nombre=nombre
            )

            servicio.categoria_fk_id = categoria.id
            servicio.save(
                using=db,
                update_fields=['categoria_fk']
            )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_categoria_servicio_categoria_fk'),
    ]

    operations = [
        migrations.RunPython(
            migrar_categorias,
            migrations.RunPython.noop
        ),
    ]
