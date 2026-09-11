"""Carga y validación centralizada de datos para Vigía RH.

Un solo lugar define qué columnas necesita el pipeline actual
(dashboard, índice JD-R, modelo y reportes) y cómo se calcula el
índice compuesto inspirado conceptualmente en el modelo Job
Demands-Resources (JD-R). Ese índice NO es un instrumento
psicométrico validado (no es MBI ni equivalente).
"""

import os

import pandas as pd

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)
RUTA_DATOS_DEFAULT = os.path.join(
    PROJECT_ROOT, "data", "WA_Fn-UseC_-HR-Employee-Attrition.csv"
)

# Columnas que hoy usa el producto. El modelo puede usar más si existen.
COLUMNAS_REQUERIDAS = [
    "Attrition",
    "OverTime",
    "JobSatisfaction",
    "MonthlyIncome",
    "Department",
    "DistanceFromHome",
    "WorkLifeBalance",
    "RelationshipSatisfaction",
]


def validar_columnas(df: pd.DataFrame) -> None:
    """Falla con un mensaje claro si faltan columnas del esquema mínimo."""
    faltantes = [col for col in COLUMNAS_REQUERIDAS if col not in df.columns]
    if faltantes:
        raise ValueError(
            "El archivo no tiene las columnas necesarias: "
            f"{faltantes}. El pipeline espera estos nombres exactos "
            f"(esquema IBM HR Analytics): {COLUMNAS_REQUERIDAS}."
        )

    if "Attrition" in df.columns:
        valores = set(df["Attrition"].dropna().unique())
        if not valores.issubset({"Yes", "No"}):
            raise ValueError(
                "La columna Attrition debe usar los valores 'Yes' y 'No' "
                f"(se encontraron: {sorted(valores)})."
            )


def cargar_datos(ruta: str | None = None) -> pd.DataFrame:
    """Lee el CSV, valida columnas y devuelve el DataFrame."""
    ruta_archivo = ruta or RUTA_DATOS_DEFAULT
    if not os.path.isfile(ruta_archivo):
        raise FileNotFoundError(
            f"No se encontró el archivo de datos en: {ruta_archivo}. "
            "Coloca el CSV en data/ o pasa una ruta válida."
        )
    df = pd.read_csv(ruta_archivo)
    validar_columnas(df)
    return df


def agregar_indice_compuesto_jdr(df: pd.DataFrame) -> pd.DataFrame:
    """Añade un índice compuesto inspirado conceptualmente en JD-R.

    Fórmula (demandas altas + recursos bajos), no un test clínico:
    horas extra (peso 2) + (5 - satisfacción) + (5 - balance) + (5 - relación con jefe).
    """
    out = df.copy()
    demanda_horas_extra = out["OverTime"].map({"Yes": 1, "No": 0})
    if demanda_horas_extra.isna().any():
        raise ValueError(
            "OverTime debe ser 'Yes' o 'No' para calcular el índice compuesto JD-R."
        )
    out["indice_compuesto_jdr"] = (
        demanda_horas_extra * 2
        + (5 - out["JobSatisfaction"])
        + (5 - out["WorkLifeBalance"])
        + (5 - out["RelationshipSatisfaction"])
    )
    return out
