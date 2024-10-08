# Generated by Django 5.0.9 on 2024-09-10 12:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('alumnos', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='alumno',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='inhabilitacion',
            name='id_alumno',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alumnos.alumno'),
        ),
        migrations.AddField(
            model_name='inhabilitacion',
            name='id_tipo_inhabilitacion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alumnos.tipoinhabilitacion'),
        ),
    ]
