# Generated by Django 5.0.9 on 2024-09-16 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagos', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pago',
            old_name='monto',
            new_name='monto_informado',
        ),
        migrations.RemoveField(
            model_name='pago',
            name='comprobante',
        ),
        migrations.RemoveField(
            model_name='pago',
            name='cuota',
        ),
        migrations.AddField(
            model_name='pago',
            name='ticket',
            field=models.ImageField(blank=True, null=True, upload_to='tickets/'),
        ),
    ]