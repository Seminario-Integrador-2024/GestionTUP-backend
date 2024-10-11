# Generated by Django 5.0.9 on 2024-10-09 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Materia',
            fields=[
                ('codigo_materia', models.IntegerField(primary_key=True, serialize=False)),
                ('anio_cursada', models.PositiveSmallIntegerField()),
                ('anio_plan', models.PositiveSmallIntegerField(default=2024)),
                ('nombre', models.CharField(max_length=255)),
                ('cuatrimestre', models.PositiveSmallIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='MateriaAlumno',
            fields=[
                ('id_materia_alumno', models.AutoField(primary_key=True, serialize=False)),
                ('anio', models.IntegerField()),
                ('offrc', models.IntegerField()),
                ('atendnc', models.IntegerField()),
            ],
        ),
    ]
