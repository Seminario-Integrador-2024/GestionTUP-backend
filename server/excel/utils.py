"""
Utils for excel_sysacad app

A. Validar formato archivo sysacad xls
0. recibir archivo sysacad via http post
1. abrir archivo sysacad
2. leer archivo sysacad via pandas
3.0 validar los campos del archivo sysacad
_reglas:

3.0.1. DNI numerico de 7 a 8 dígitos;
3.0.2. nombre y apellido no vacíos, solo letras, espacios,letra 'ñ',\
    y acentos en vocales;
3.0.3 email válido;
3.0.4 celular de 10 dígitos numerico,
3.0.5 teléfono de 7 a 8 dígitos numerico
3.0.6
3.0.7 ingreso y año de 4 digitos numerico
3.0.8 esp 2 digitos numerico
3.0.9 leg 5 digitos numerico
3.1 si algun campo no es válido, indicar fila y columna del error o errores

B. cargar archivo sysacad xls en la bbdd
0. recibir archivo sysacad validado
1. abrir archivo sysacad
2. leer archivo sysacad, registro a registro, via pandas
3. insertar registros a la bbdd:
4. para cada registro:
4.1. si el alumno ya existe en la bbdd (DNI), ignorarlo.
4.2 si el alumno no existe en la bbdd, agregarlo.
4.3 idem 4.1 y 4.2 para las materias (Materia) .
4.4 idem 4.1 y 4.2 para Materia_Alumno(DNI,Materia,Año).
5 reporte de registros duplicados de Materia_Alumno
6 reporte de registros agregados de Materia_Alumno
"""

import re
from typing import TYPE_CHECKING
import json
import pandas as pd
from django.db import transaction

if TYPE_CHECKING:
    from collections.abc import Callable


# functions definitions


def validate_excel(data: pd.DataFrame) -> dict:
    """
    Validates the data in a DataFrame against a set lambda functions.

    Args:
        data (pd.DataFrame): The DataFrame to validate.

    Returns:
        dict: A dict containing the invalid rows if any, sorted by row number.
    """
    # compile the regex patterns
    regex_extension = r"^\s*0\s*$"
    regex_esp = r"^\s*34\s*$"
    regex_ingr = r"^\s*20\d\d\s*$"
    regex_anio = regex_ingr
    regex_legajo = r"^[\s]*[1-9]\d{4}[\s]*$"
    regex_dni = r"^\s*\d{7,8}\s*$"
    regex_nombres = r"[\s]*([a-zàáèéìíòóùúñçA-ZÀÁÈÉÌÍÒÓÙÚÑ]+[\s]*)+"
    regex_ap_no = regex_nombres + r"[\s]*,?[\s]*" + regex_nombres
    regex_comision = r"^\s*\d\s*$"
    regex_materia = r"^\s*\d\d\d\s*$"
    regex_no_ma = regex_nombres
    regex_estado = r"^\s*Inscripto\s*$"
    regex_recursa = r"^\s*(Si|No)\s*$"
    regex_mail = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)?"
    regex_telefono = r"((\d{0,4}-?)?\d{6,10})?"
    regex_notas = r"([\s]*[1-9]([\.,]\d{1,2})?|10[\s]*)?"
    regex_activo = r"^\s*Activo\s*$"
    # Define the rules
    rules: dict[str, Callable] = {
        "Extensión": lambda x: bool(re.compile(regex_extension).match(str(x))),
        "Esp.": lambda x: bool(re.compile(regex_esp).match(str(x))),
        "Ingr.": lambda x: bool(re.compile(regex_notas).match(str(x))),
        "Año": lambda x: bool(re.compile(regex_anio).match(str(x))),
        "Legajo": lambda x: bool(re.compile(regex_legajo).match(str(x))),
        "Documento": lambda x: bool(re.compile(regex_dni).match(str(x))),
        "Apellido y Nombres": lambda x: bool(
            re.match(
                regex_ap_no,
                str(x),
            )
        ),
        "Comisión": lambda x: bool(re.compile(regex_comision).match(str(x))),
        "Materia": lambda x: bool(re.compile(regex_materia).match(str(x))),
        "Nombre de materia": lambda x: bool(
            re.match(
                regex_no_ma,
                str(x),
            )
        ),
        "Estado": lambda x: bool(re.compile(regex_estado).match(str(x))),
        "Recursa": lambda x: bool(re.compile(regex_recursa).match(str(x))),
        "Cant.": lambda x: isinstance(x, int) and x >= 0,
        "Mail": lambda x: re.compile(regex_mail).match(str(x)),
        "Celular": lambda x: bool(re.compile(regex_telefono).match(str(x))),
        "Teléfono": lambda x: bool(re.compile(regex_telefono).match(str(x))),
        "Tel. Resid": lambda x: pd.isna(x)
        or bool(re.compile(regex_telefono).match(str(x))),
        "Nota 1": lambda x: bool(re.compile(regex_notas).match(str(x))),
        "Nota 2": lambda x: bool(re.compile(regex_notas).match(str(x))),
        "Nota 3": lambda x: bool(re.compile(regex_notas).match(str(x))),
        "Nota 4": lambda x: bool(re.compile(regex_notas).match(str(x))),
        "Nota 5": lambda x: bool(re.compile(regex_notas).match(str(x))),
        "Nota 6": lambda x: bool(re.compile(regex_notas).match(str(x))),
        "Nota 7": lambda x: bool(re.compile(regex_notas).match(str(x))),
        "Nota Final": lambda x: bool(re.compile(regex_notas).match(str(x))),
        "Nombre": lambda x: bool(re.compile(regex_activo).match(str(x))),
    }

    # Validate the data and track errors
    def validate_row(row):
        errors = {}
        for col, rule in rules.items():
            if not rule(row[col]):  # If the rule is not satisfied
                errors[col] = row.name  # Index of the row
        return errors

    invalid_rows = data.apply(
        validate_row, axis=1
    )  # Apply the validation to each row and store the errors
    invalid_rows = (  # Convert the
        # errors to a DataFrame with the column names and row numbers
        pd.DataFrame(
            invalid_rows.tolist()  # Convert
            # the list of dictionaries to a list of lists
        )  # Convert the list of dictionaries to a DataFrame
        .stack()  # Stack the columns to get a multi-index DataFrame
        .reset_index(level=1)  # Reset the index to get the
        # column names as a column instead of the index
        .rename(columns={0: "row"})  # Rename the column to "row"
    )  # Convert the multi-index DataFrame to a single-index DataFrame
    invalid_rows.columns = [
        "columna",
        "error_en_fila",
    ]
    # Convert the DataFrame to a dictionary for JSON serialization
    my_dict: dict = json.loads(
        invalid_rows.pivot(
            index="error_en_fila", columns="columna", values="columna"
        ).to_json(orient="index")
    )
    return my_dict


# cargar archivo sysacad xls en la bbdd


def load_data(data: pd.DataFrame):
    """
    Load Excel data into the database.

    Args:
    - data (pd.DataFrame): The data to load into the database.
    """
    # models definitions
    from server.alumnos.models import Alumno
    from server.materias.models import Materia
    from server.materias.models import MateriaAlumno
    from server.users.models import User

    # sanitize the data

    # iterate over the rows, create the instances and save them
    for _, row in data.iterrows():
        # 36770618
        # if create use Model.objets.create()
        # if create or update use Model() and then Model.save()
        # create the Alumno instance
        # add onetone user field
        if pd.isna(row["Teléfono"]):
            row["Teléfono"] = "N/A"
        if pd.isna(row["Tel. Resid"]):
            row["Tel. Resid"] = "N/A"
        if pd.isna(row["Celular"]):
            row["Celular"] = "N/A"
        if pd.isna(row["Mail"]):
            row["Mail"] = "N/A"
        alumno = Alumno(
            user=User(
                dni=row["Documento"],
                email=row["Mail"],
                full_name=row["Apellido y Nombres"],
            ),
            estado=row["Estado"],
            legajo=row["Legajo"],
            anio_ingreso=row["Ingr."],
            tel_res=row["Tel. Resid"],
            telefono=str(row["Teléfono"]),
            celular=str(row["Celular"]),
        )
        # create the Materia instance
        materia = Materia(
            codigo_materia=row["Materia"],
            anio_cursada=row["Año"],
            nombre=row["Nombre de materia"],
        )
        # create the MateriaAlumno instance
        materia_alumno = MateriaAlumno(
            id_materia=materia,
            id_alumno=alumno,
            anio=row["Año"],
            offrc=0,
            atendnc=0,
        )
        # save the instances
        with transaction.atomic():
            if not User.objects.filter(dni=alumno.user.dni).exists():
                alumno.user.save()
                alumno.save()
            if not Materia.objects.filter(
                codigo_materia=materia.codigo_materia,
            ).exists():
                materia.save()
                materia_alumno.id_alumno.save()
                materia_alumno.save()


if __name__ == "__main__":
    # Call the main function

    from pathlib import Path
    from tkinter import filedialog as fd

    # get file by filedialog, http post or other method
    path: str = fd.askopenfilename(
        title="Elija Archivo excel a validar",
        initialdir=Path().home() / "Downloads",
        filetypes=(("Excel files", "*.xls *.xlsx"), ("all files", "*.*")),
    )

    # read the file
    COL_HEADER = 6  # header row with column names in the excel file
    df: pd.DataFrame = pd.read_excel(
        io=path,
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
        skiprows=COL_HEADER - 1,
        engine="openpyxl",
    )
    # make index start at 6
    df.index = df.index + COL_HEADER + 1
    # result: dict = validate_excel(df)
    # do something with result
    print(df.iloc[0:20, 10:17].head(20))
