# Generated by Django 5.0.9 on 2024-09-26 05:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alumno',
            fields=[
                ('user', models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('estado', models.CharField(choices=[('0', 'Activo'), ('1', 'Inactivo'), ('2', 'Egresado'), ('3', 'Inhabilitado')], default='Activo')),
                ('legajo', models.PositiveIntegerField(default=0, unique=True, verbose_name='Legajo')),
                ('anio_ingreso', models.IntegerField()),
                ('telefono', models.CharField(blank=True)),
                ('tel_res', models.CharField(blank=True)),
                ('celular', models.CharField(blank=True)),
                ('gender', models.CharField(choices=[('M', 'male'), ('F', 'female')], default='M', max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='TipoEstado',
            fields=[
                ('id_tipo_estado', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=255)),
                ('descripcion', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='TipoInhabilitacion',
            fields=[
                ('id_tipo_inhabilitacion', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=255)),
                ('descripcion', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Inhabilitacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_desde', models.DateTimeField()),
                ('fecha_hasta', models.DateTimeField()),
                ('descripcion', models.TextField()),
                ('id_alumno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alumnos.alumno')),
                ('id_tipo_inhabilitacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alumnos.tipoinhabilitacion')),
            ],
        ),
    ]
