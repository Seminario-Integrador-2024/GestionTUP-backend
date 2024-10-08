# Generated by Django 5.0.9 on 2024-09-10 20:04

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('excel', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='excel',
            name='excel',
            field=models.FileField(help_text='Only Excel files (.xlsx, .xls) are allowed', upload_to='excels/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])]),
        ),
    ]
