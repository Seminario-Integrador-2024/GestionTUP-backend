# Generated by Django 5.0.9 on 2024-10-07 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alumnos', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TipoEstado',
        ),
        migrations.RemoveField(
            model_name='inhabilitacion',
            name='id_tipo_inhabilitacion',
        ),
        migrations.AlterField(
            model_name='inhabilitacion',
            name='fecha_hasta',
            field=models.DateTimeField(blank=True),
        ),
        migrations.DeleteModel(
            name='TipoInhabilitacion',
        ),
    ]
