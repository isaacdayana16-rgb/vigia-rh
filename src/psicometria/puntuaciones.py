"""Cálculo de puntuaciones por dimensión (Job Demands / Job Resources).

Aplica codificación inversa cuando corresponde y calcula la media por
dimensión. NO combina demandas y recursos en un índice único.
"""
import numpy as np
import pandas as pd

from .instrumento import ITEMS, DIMENSIONES, items_de_dimension


def validar_datos_respuestas(df: pd.DataFrame) -> dict:
    """Valida la estructura de un archivo de respuestas.

    Comprueba qué ítems del instrumento están presentes y si existe la
    columna de outcome ('intencion_rotacion'). No modifica el DataFrame.

    Args:
        df: DataFrame con columnas = ids de ítems (y opcionalmente outcome).

    Returns:
        dict con:
            'presentes': lista de ids de ítems presentes.
            'faltantes': lista de ids de ítems requeridos ausentes.
            'tiene_outcome': bool si existe 'intencion_rotacion'.
            'total_items_instrumento': número de ítems del instrumento.
    """
    presentes = [iid for iid in ITEMS if iid in df.columns]
    faltantes = [iid for iid in ITEMS if iid not in df.columns]
    return {
        "presentes": presentes,
        "faltantes": faltantes,
        "tiene_outcome": "intencion_rotacion" in df.columns,
        "total_items_instrumento": len(ITEMS),
    }


def aplicar_reversa(serie: pd.Series, escala: int = 1, maximo: int = 5) -> pd.Series:
    """Invierte una serie Likert: puntuación = maximo + escala - valor.

    Args:
        serie: Serie con valores en escala Likert.
        escala: Valor mínimo de la escala (default 1).
        maximo: Valor máximo de la escala (default 5).

    Returns:
        Serie con los valores invertidos.
    """
    return maximo + escala - serie


def calcular_puntuaciones(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula la puntuación media por dimensión (demandas y recursos).

    Args:
        df: DataFrame con columnas = ids de ítems (Likert 1-5).
            Puede contener columnas extra (criterio, etc.) que se ignoran.

    Returns:
        DataFrame con columnas 'demandas' y 'recursos' (medias 1-5).
    """
    out = pd.DataFrame(index=df.index)
    for dimension in DIMENSIONES:
        ids = [iid for iid in items_de_dimension(dimension) if iid in df.columns]
        if not ids:
            out[dimension] = np.nan
            continue
        temp = df[ids].copy()
        for iid in ids:
            if ITEMS[iid]["reversa"]:
                temp[iid] = aplicar_reversa(temp[iid])
        out[dimension] = temp.mean(axis=1)
    return out