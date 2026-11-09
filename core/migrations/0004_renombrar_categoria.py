# migrations: herramientas de Django para escribir migraciones a mano
from django.db import migrations


# class Migration: Django la generó con "makemigrations --empty"; solo cambias "operations"
class Migration(migrations.Migration):

    # dependencies: DÉJALA COMO LA ESCRIBIÓ DJANGO; debe apuntar a la migración copiar_categorias
    dependencies = [
        # ejemplo: la migración del paso 03; en tu archivo puede tener otro número
        ('core', '0003_copiar_categorias'),
    # cierra la lista de dependencias
    ]

    # operations: se ejecutan en orden, de arriba hacia abajo
    operations = [
        # 1) RemoveField: borra la columna de TEXTO "categoria" (ya se copió a categoria_ref en el paso 03)
        migrations.RemoveField(model_name='servicio', name='categoria'),
        # 2) RenameField: cambia el nombre categoria_ref → categoria; los datos y la llave foránea se conservan
        migrations.RenameField(model_name='servicio', old_name='categoria_ref', new_name='categoria'),
    # cierra la lista de operaciones
    ]