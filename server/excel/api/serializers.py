import pandas as pd
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ParseError
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from server.excel.models import Excel
from server.excel.utils import load_data
from server.excel.utils import validate_excel


class InvalidFileContents(APIException):
    """
    Error: Invalid Excel file format

    Returns:
        detail: Invalid rows in the Excel file
    """

    status_code = 412
    default_detail = "Excel format is invalid"
    default_code = "invalid_rows"


class ExcelCreateSerializer(ModelSerializer):
    class Meta:
        model = Excel
        fields = ("excel",)

    def validate_excel(self, value):
        allowed_extensions = ["xlsx", "xls"]
        if not value.name.endswith(tuple(allowed_extensions)):
            msg = f"File extension not allowed. Allowed extensions: \
                {', '.join(allowed_extensions)}"
            raise ValidationError(detail=msg, code="invalid_file_extension")

        try:
            col_header = 6
            excel_as_df = pd.read_excel(
                io=value,
                # header=col_header,
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
                # skiprows=col_header - 1,
                engine="openpyxl",
            )
        except pd.errors.EmptyDataError as e:
            msg = f"Empty Excel file: {e!s}"
            raise ValidationError(
                msg,
                code="empty_excel_file",
            )
        except pd.errors.ParserError as e:
            msg = f"Invalid Excel file: {e!s}"
            raise ParseError(
                msg,
                code="invalid_excel_file",
            )

        excel_as_df.index = excel_as_df.index + col_header + 1
        # Validate Excel file format and return invalid rows
        invalid_rows_dict = validate_excel(excel_as_df)

        if invalid_rows_dict:
            raise InvalidFileContents(detail=invalid_rows_dict)

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
            self.context["duplicates"] = duplicates.shape[0]

        # Load data to the database
        load_data(excel_as_df)

        if duplicates.empty:
            self.context["message"] = (
                "Data and Excel successfully loaded without duplicates"
            )
        else:
            tot_dup = duplicates.shape[0]
            self.context["amount"] = tot_dup
            self.context["message"] = (
                "Data and Excel loaded successfully. Duplicate rows were\
                    identified and not added to the database."
            )
        self.context["total"] = excel_as_df.shape[0]
        return value

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if "amount" in self.context:
            ret["duplicates"] = self.context["amount"]
        if "message" in self.context:
            ret["message"] = self.context["message"]
            ret["total"] = self.context["total"]
        return ret


class ExcelListSerializer(ModelSerializer):
    class Meta:
        model = Excel
        fields = "__all__"
