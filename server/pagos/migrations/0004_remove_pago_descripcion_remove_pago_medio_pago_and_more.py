# Generated by Django 5.0.9 on 2024-09-21 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagos', '0003_alter_compromisodepago_anio_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pago',
            name='descripcion',
        ),
        migrations.RemoveField(
            model_name='pago',
            name='medio_pago',
        ),
        migrations.RemoveField(
            model_name='pago',
            name='nro_recibo',
        ),
        migrations.AlterField(
            model_name='pago',
            name='estado',
            field=models.CharField(),
        ),
    ]
