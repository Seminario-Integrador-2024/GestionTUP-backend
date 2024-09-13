import pandas as pd
from rest_framework.serializers import ModelSerializer, ValidationError
from rest_framework.response import Response
from rest_framework import status
from server.excel.models import Excel
from server.excel.utils import load_data
from server.excel.utils import validate_excel_file


class ExcelInvalidContentValidationError(ValidationError):
    status_code = status.HTTP_412_PRECONDITION_FAILED
    default_code = "invalid_excel_contents"


class ExcelCreateSerializer(ModelSerializer):
    class Meta:
        model = Excel
        # fields = ("excel",)
        fields = "__all__"

    def validate_excel(self, value):
        allowed_extensions = ["xlsx", "xls"]
        if not value.name.endswith(tuple(allowed_extensions)):
            msg = f"File extension not allowed. Allowed extensions: \
                {', '.join(allowed_extensions)}"
            raise ValidationError(msg, code="invalid_file_extension")

        try:
            col_header = 6
            excel_as_df: pd.DataFrame = pd.read_excel(
                io=value,
                header=col_header - 1,
                names=[
                    "Extensión",
                    "Esp.",
                    "Ingr.",
                    "Año",
                    "Legajo",
                    "Documento",
                    "Apellido y Nombres",
                    "Comisión",
                    "Materia",
                    "Nombre de materia",
                    "Estado",
                    "Recursa",
                    "Cant.",
                    "Mail",
                    "Celular",
                    "Teléfono",
                    "Tel. Resid",
                    "Nota 1",
                    "Nota 2",
                    "Nota 3",
                    "Nota 4",
                    "Nota 5",
                    "Nota 6",
                    "Nota 7",
                    "Nota Final",
                    "Nombre",
                ],
                skiprows=col_header - 1,
                engine="openpyxl",
            )
        except ValueError as e:
            msg = f"Invalid Excel file: {e!s}"
            raise ValidationError(
                msg,
                code="invalid_excel_file",
            ) from e

        excel_as_df.index = excel_as_df.index + col_header + 1

        # Validate Excel file format and return invalid rows

        result = validate_excel_file(excel_as_df)

        if not result.empty or result is not None:
            raise ExcelInvalidContentValidationError(
                detail=result.to_dict(), code="invalid_excel_contents"
            )
        # Check for duplicates
        columns_filter = ["Documento", "Materia", "Año"]
        duplicates = excel_as_df[
            excel_as_df.duplicated(subset=columns_filter, keep="last")
        ]

        if not duplicates.empty:
            excel_as_df = excel_as_df.drop_duplicates(
                subset=columns_filter,
                keep="last",
            )
            self.context["duplicates"] = duplicates.to_dict(orient="index")

        # Load data to the database
        load_data(excel_as_df)

        if duplicates.empty:
            self.context["message"] = (
                "Data successfully loaded\
                without duplicates"
            )
        else:
            self.context["message"] = (
                "Data loaded successfully. \
                    Duplicate rows were identified\
                        and not added to the database."
            )

        return value

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if "duplicates" in self.context:
            ret["duplicates"] = self.context["duplicates"]
        if "message" in self.context:
            ret["message"] = self.context["message"]
        return ret


class ExcelListSerializer(ModelSerializer):
    class Meta:
        model = Excel
        fields = "__all__"
