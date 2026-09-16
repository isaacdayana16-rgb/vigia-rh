"""Validación de calidad de datos de encuesta.

Detecta problemas comunes en datos reales recolectados por formularios antes
de ejecutar la validación psicométrica:

- Valores fuera del rango Likert (1-5) en ítems.
- Filas con datos faltantes (NaN) en ítems.
- Columnas mal nombradas (ítems ausentes / columnas desconocidas).
- Filas duplicadas exactas (posible doble envío).
- Ítems con varianza nula (no discriminan; rompen el análisis factorial).
- Outcome ('intencion_rotacion') mal codificado.

Esto reduce errores espurios en fiabilidad (alpha/omega) y validez (AFE).
"""
import numpy as np
import pandas as pd

from .instrumento import ITEMS


def _items_presentes(df: pd.DataFrame) -> list:
    """Ids de ítems del instrumento presentes en el DataFrame."""
    return [iid for iid in ITEMS if iid in df.columns]


def validar_rango_items(df: pd.DataFrame, minimo: int = 1, maximo: int = 5) -> dict:
    """Detecta ítems con valores fuera del rango Likert [minimo, maximo].

    Returns:
        dict con 'items_afectados' (lista de ids) y 'valores_fuera' (DataFrame
        con las filas/valores problemáticos), o vacío si todo está en rango.
    """
    ids = _items_presentes(df)
    fuera = {}
    for iid in ids:
        serie = df[iid]
        mascara = serie.notna() & ~serie.between(minimo, maximo)
        if mascara.any():
            fuera[iid] = serie[mascara].unique().tolist()
    return {"items_afectados": list(fuera.keys()), "valores_fuera": fuera}


def detectar_filas_incompletas(df: pd.DataFrame) -> pd.DataFrame:
    """Detecta filas con valores faltantes (NaN) en ítems del instrumento.

    Returns:
        DataFrame con las filas incompletas (idices originales y nº de NaN).
    """
    ids = _items_presentes(df)
    if not ids:
        return pd.DataFrame(columns=["indice", "n_nan"])
    nan_por_fila = df[ids].isna().sum(axis=1)
    incompletas = nan_por_fila[nan_por_fila > 0]
    return pd.DataFrame({"indice": incompletas.index, "n_nan": incompletas.values})


def detectar_columnas_problema(df: pd.DataFrame) -> dict:
    """Detecta ítems ausentes y columnas que no pertenecen al instrumento.

    Returns:
        dict con 'items_faltantes' y 'columnas_desconocidas'.
    """
    esperadas = set(ITEMS.keys())
    presentes = set(df.columns)
    return {
        "items_faltantes": sorted(esperadas - presentes),
        "columnas_desconocidas": sorted(
            presentes - esperadas - {"intencion_rotacion"}
        ),
    }


def detectar_duplicados(df: pd.DataFrame) -> pd.DataFrame:
    """Detecta filas duplicadas exactas en todos los ítems.

    Returns:
        DataFrame con las filas duplicadas (indices y conteo).
    """
    ids = _items_presentes(df)
    if not ids:
        return pd.DataFrame(columns=["indice", "conteo"])
    dup = df[df.duplicated(subset=ids, keep=False)]
    conteo = dup.groupby(list(ids)).size().reset_index(name="conteo")
    return conteo


def detectar_items_varianza_cero(df: pd.DataFrame) -> list:
    """Detecta ítems con varianza nula (no discriminan, rompen el AFE).

    Returns:
        Lista de ids de ítems con varianza (ddof=1) igual a 0.
    """
    ids = _items_presentes(df)
    var = df[ids].var(axis=0, ddof=1)
    return [iid for iid in ids if iid in var.index and var[iid] == 0]


def validar_outcome(df: pd.DataFrame) -> dict:
    """Valida la columna de outcome ('intencion_rotacion').

    Returns:
        dict con 'presente' (bool) y, si está presente, 'es_binario',
        'valores_unicos' y 'proporcion_clase_1'.
    """
    if "intencion_rotacion" not in df.columns:
        return {"presente": False}
    serie = df["intencion_rotacion"].dropna()
    if serie.empty:
        return {"presente": True, "es_binario": False, "valores_unicos": [], "proporcion_clase_1": None}
    valores = serie.unique().tolist()
    es_binario = set(valores).issubset({0, 1})
    proporcion = float(serie.mean()) if es_binario else None
    return {
        "presente": True,
        "es_binario": es_binario,
        "valores_unicos": valores,
        "proporcion_clase_1": proporcion,
    }


def reporte_calidad_datos(df: pd.DataFrame) -> dict:
    """Consolida todos los controles de calidad en un reporte.

    Returns:
        dict con un resumen de cada control y una lista de advertencias.
    """
    rango = validar_rango_items(df)
    incompletas = detectar_filas_incompletas(df)
    columnas = detectar_columnas_problema(df)
    duplicados = detectar_duplicados(df)
    varianza_cero = detectar_items_varianza_cero(df)
    outcome = validar_outcome(df)

    advertencias = []
    if rango["items_afectados"]:
        advertencias.append(
            f"{len(rango['items_afectados'])} ítem(s) con valores fuera del rango 1-5."
        )
    if not incompletas.empty:
        advertencias.append(f"{len(incompletas)} fila(s) con datos faltantes en ítems.")
    if columnas["items_faltantes"]:
        advertencias.append(
            f"Faltan {len(columnas['items_faltantes'])} ítem(s) del instrumento."
        )
    if not duplicados.empty:
        advertencias.append(f"Se detectaron filas duplicadas (posible doble envío).")
    if varianza_cero:
        advertencias.append(
            f"{len(varianza_cero)} ítem(s) con varianza nula (no discriminan; rompen el AFE)."
        )
    if outcome["presente"] and not outcome["es_binario"]:
        advertencias.append(
            f"La columna 'intencion_rotacion' no es binaria (valores: {outcome['valores_unicos']})."
        )

    return {
        "n_filas": len(df),
        "rango_items": rango,
        "filas_incompletas": len(incompletas),
        "columnas": columnas,
        "duplicados": len(duplicados),
        "items_varianza_cero": varianza_cero,
        "outcome": outcome,
        "advertencias": advertencias,
    }