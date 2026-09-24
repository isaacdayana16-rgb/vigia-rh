"""Cálculo de puntuaciones del instrumento oficial MDT (sumatoria simple).

Método oficial (Guía MDT-Ecuador, págs. 10-11): sumatoria simple de los
ítems que integran cada dimensión (Tabla 2), comparada con los puntos de
corte de la Tabla 3. La suma global (58 ítems) se compara con la Tabla 4.
Menor puntaje = mayor riesgo.

Con `normalizar=True` retorna la media por ítem (1-4) para comparabilidad
entre dimensiones de distinto largo (gráficos, coeficientes).

Conforme al instrumento oficial, es obligatorio contestar todos los ítems:
si falta alguno (o es "NR"), la puntuación de esa dimensión es faltante
(NaN) en lugar de una suma parcial que distorsionaría los puntos de corte.
"""
import numpy as np
import pandas as pd

from .instrumento import (
    ITEMS,
    DIMENSIONES,
    SUBESCALAS_OTROS,
    items_de_dimension,
    items_de_subescala,
)


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


def aplicar_reversa(serie: pd.Series, escala: int = 1, maximo: int = 4) -> pd.Series:
    """Invierte una serie Likert: puntuación = maximo + escala - valor.

    Los ítems del instrumento oficial no requieren reversa (todos están
    redactados en dirección positiva); se conserva como utilidad genérica.

    Args:
        serie: Serie con valores en escala Likert.
        escala: Valor mínimo de la escala (default 1).
        maximo: Valor máximo de la escala (default 4).

    Returns:
        Serie con los valores invertidos.
    """
    return maximo + escala - serie


def _suma_items(df: pd.DataFrame, ids: list) -> pd.Series:
    """Suma los ítems de una lista, exigiendo todos los valores presentes.

    Convierte a numérico (texto "NR" o vacío -> NaN) y retorna NaN si falta
    algún ítem de la lista, conforme a la regla oficial de respuesta completa.
    """
    temp = df[ids].apply(pd.to_numeric, errors="coerce")
    return temp.sum(axis=1, min_count=len(ids))


def calcular_puntuaciones(df: pd.DataFrame, normalizar: bool = False) -> pd.DataFrame:
    """Calcula la puntuación por dimensión (sumatoria simple, método oficial).

    Args:
        df: DataFrame con columnas = ids de ítems (Likert 1-4).
            Puede contener columnas extra (datos generales, criterio) que se ignoran.
        normalizar: Si True, retorna la media por ítem (1-4) en lugar de la suma.

    Returns:
        DataFrame con una columna por dimensión (sumas oficiales o medias).
    """
    out = pd.DataFrame(index=df.index)
    for dimension in DIMENSIONES:
        ids_oficiales = items_de_dimension(dimension)
        ids = [iid for iid in ids_oficiales if iid in df.columns]
        if len(ids) < len(ids_oficiales):
            # Faltan ítems oficiales de la dimensión: una suma parcial
            # distorsionaría los puntos de corte oficiales.
            out[dimension] = np.nan
            continue
        suma = _suma_items(df, ids)
        out[dimension] = suma / len(ids) if normalizar else suma
    return out


def calcular_puntuaciones_subescala(df: pd.DataFrame, normalizar: bool = False) -> pd.DataFrame:
    """Calcula la puntuación por subescala de 'Otros puntos importantes'.

    Args:
        df: DataFrame con columnas = ids de ítems (Likert 1-4).
        normalizar: Si True, retorna la media por ítem (1-4) en lugar de la suma.

    Returns:
        DataFrame con una columna por subescala (sumas oficiales o medias).
    """
    out = pd.DataFrame(index=df.index)
    for subescala in SUBESCALAS_OTROS:
        ids_oficiales = items_de_subescala(subescala)
        ids = [iid for iid in ids_oficiales if iid in df.columns]
        if len(ids) < len(ids_oficiales):
            out[subescala] = np.nan
            continue
        suma = _suma_items(df, ids)
        out[subescala] = suma / len(ids) if normalizar else suma
    return out


def calcular_suma_global(df: pd.DataFrame) -> pd.Series:
    """Calcula la suma global de los 58 ítems (Tabla 4 del PDF oficial).

    Requiere los 58 ítems presentes y completos; si falta alguno, retorna
    una serie de NaN (la clasificación global oficial no admite sumas parciales).

    Returns:
        pd.Series con la suma global (rango teórico 58-232).
    """
    ids = [iid for iid in ITEMS if iid in df.columns]
    if len(ids) < len(ITEMS):
        return pd.Series(np.nan, index=df.index)
    return _suma_items(df, ids)
