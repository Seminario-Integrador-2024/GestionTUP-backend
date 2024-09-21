# Generated by Django 5.0.9 on 2024-09-16 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagos', '0002_rename_monto_pago_monto_informado_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compromisodepago',
            name='anio',
            field=models.DateTimeField(max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='compromisodepago',
            name='cuatrimestre',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='compromisodepago',
            name='cuota_reducida',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='compromisodepago',
            name='cuota_reducida_2venc',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='compromisodepago',
            name='cuota_reducida_3venc',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='compromisodepago',
            name='fecha_vencimiento_1',
            field=models.IntegerField(default=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='compromisodepago',
            name='fecha_vencimiento_2',
            field=models.IntegerField(default=15),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='compromisodepago',
            name='fecha_vencimiento_3',
            field=models.IntegerField(default=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='compromisodepago',
            name='matricula',
            field=models.FloatField(default=123),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='compromisodepago',
            name='monto_completo',
            field=models.FloatField(default=123123),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='compromisodepago',
            name='monto_completo_2venc',
            field=models.FloatField(default=123123),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='compromisodepago',
            name='monto_completo_3venc',
            field=models.FloatField(default=121232),
            preserve_default=False,
        ),
    ]
