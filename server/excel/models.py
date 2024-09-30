from datetime import datetime
from venv import logger

from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.signals import pre_delete
from django.db.models.signals import pre_save
from django.dispatch import receiver


# Create your models here.
class Excel(models.Model):
    excel = models.FileField(
        upload_to="excels/",
        validators=[
            FileExtensionValidator(allowed_extensions=["xlsx", "xls"]),
        ],
        help_text="Only Excel files (.xlsx, .xls) are allowed",
    )
    uploaded_at = models.DateTimeField(
        auto_created=True,
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Excel"
        verbose_name_plural = "Excels"

    def __str__(self):
        return self.excel.name


@receiver([pre_save], sender=Excel)
def excel_pre_save(sender, instance, **kwargs):
    instance.uploaded_at = datetime.now()
    ext = instance.excel.name.split(".")[-1]
    format = "%Y_%m_%d_%H_%M"
    logger.info(f"Excel {instance.excel.name} has been uploaded.")
    instance.excel.name = f"{instance.uploaded_at.strftime(format)}.{ext}"


@receiver([pre_delete], sender=Excel)
def excel_pre_delete(sender, instance, **kwargs):
    from pathlib import Path

    if instance.excel and Path.is_file(Path(instance.excel.path)):
        Path(instance.excel.path).unlink()
        logger.info(f"Excel {instance.excel.name} has been deleted.")
