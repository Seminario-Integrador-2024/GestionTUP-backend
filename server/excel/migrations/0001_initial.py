# Generated by Django 5.0.9 on 2024-09-10 18:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Excel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uploaded_at', models.DateTimeField(auto_created=True)),
                ('excel', models.FileField(upload_to='excels/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])])),
            ],
            options={
                'verbose_name': 'Excel',
                'verbose_name_plural': 'Excels',
            },
        ),
    ]
