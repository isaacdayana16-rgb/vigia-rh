"""Carga y validación centralizada de datos para Vigía RH.

Un solo lugar define qué columnas necesita el pipeline actual
(dashboard, índice JD-R, modelo y reportes) y cómo se calcula el
índice compuesto inspirado conceptualmente en el modelo Job
Demands-Resources (JD-R). Ese índice NO es un instrumento
psicométrico validado (no es MBI ni equivalente).
"""

import os

import pandas as pd

SRC_DIR = os.path.join(os.getcwd(), "src")
PROJECT_ROOT = os.getcwd()
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

MAPEO_ES = {
    "Attrition": ["Rotación", "Renuncia", "Estado", "Estado Laboral"],
    "OverTime": ["Horas Extra", "Horas Extras", "Sobretiempo"],
    "JobSatisfaction": ["Satisfacción Laboral", "Satisfacción en el Puesto"],
    "MonthlyIncome": ["Sueldo", "Salario", "Sueldo Mensual", "Salario Mensual"],
    "Department": ["Departamento", "Área"],
    "DistanceFromHome": ["Distancia al Trabajo"],
    "WorkLifeBalance": ["Balance Vida-Trabajo", "Equilibrio Vida Laboral"],
    "RelationshipSatisfaction": ["Satisfacción con el Jefe", "Relación con Supervisor"],
}

def renombrar_columnas_es(df, mapeo=MAPEO_ES):
    """Traduce columnas en español al esquema interno en inglés.
    Si ya vienen en inglés, no hace nada."""
    # Limpiar espacios en blanco de nombres de columnas
    df.columns = df.columns.str.strip()
    
    columnas_nuevas = {}
    for col_ingles, variantes in mapeo.items():
        if col_ingles in df.columns:
            continue
        for variante in variantes:
            if variante in df.columns:
                columnas_nuevas[variante] = col_ingles
                break
    return df.rename(columns=columnas_nuevas)


def detectar_mapeo_propuesto(df, mapeo=MAPEO_ES):
    """Detecta qué columnas del CSV coinciden con el mapeo.
    Retorna dict {columna_espanol: columna_ingles}."""
    mapeo_detectado = {}
    for col_ingles, variantes in mapeo.items():
        if col_ingles in df.columns:
            continue  # Ya está en inglés
        for variante in variantes:
            if variante in df.columns:
                mapeo_detectado[variante] = col_ingles
                break
    return mapeo_detectado


def mostrar_mapeo_propuesto(mapeo_detectado):
    """Formatea el mapeo detectado para visualización."""
    if not mapeo_detectado:
        return "No se detectaron columnas en español para mapear."
    
    lineas = ["Mapeo propuesto de columnas:", "Columna en español -> Columna en inglés"]
    lineas.append("-" * 50)
    for col_es, col_en in mapeo_detectado.items():
        lineas.append(f"{col_es} -> {col_en}")
    return "\n".join(lineas)


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


def cargar_datos(ruta: str | None = None, aplicar_mapeo: bool = False) -> pd.DataFrame:
    """Lee el archivo (CSV/Excel), valida columnas y devuelve el DataFrame.
    
    Args:
        ruta: Ruta al archivo. Si es None, usa RUTA_DATOS_DEFAULT.
        aplicar_mapeo: Si True, aplica renombrar_columnas_es() antes de validar.
                      Opt-in para soportar columnas en español.
    """
    ruta_archivo = ruta or RUTA_DATOS_DEFAULT
    if not os.path.isfile(ruta_archivo):
        raise FileNotFoundError(
            f"No se encontró el archivo de datos en: {ruta_archivo}. "
            "Coloca el CSV en data/ o pasa una ruta válida."
        )
    
    # Detectar formato por extensión
    extension = ruta_archivo.lower().split('.')[-1] if '.' in ruta_archivo else ''
    
    if extension in ['xlsx', 'xls']:
        df = pd.read_excel(ruta_archivo, engine='openpyxl')
    else:
        # CSV con fallback de encoding
        try:
            df = pd.read_csv(ruta_archivo)
        except UnicodeDecodeError:
            df = pd.read_csv(ruta_archivo, encoding='latin-1')
    
    if aplicar_mapeo:
        df = renombrar_columnas_es(df)
    
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
