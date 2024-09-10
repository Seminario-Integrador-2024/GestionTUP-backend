# Generated by Django 5.0.9 on 2024-09-10 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='user',
            name='id',
        ),
        migrations.RemoveField(
            model_name='user',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='user',
            name='name',
        ),
        migrations.AddField(
            model_name='user',
            name='full_name',
            field=models.CharField(blank=True, default='NonName', max_length=150, verbose_name='Full Name of User'),
        ),
        migrations.AlterField(
            model_name='user',
            name='dni',
            field=models.PositiveIntegerField(primary_key=True, serialize=False, verbose_name='DNI'),
        ),
    ]
