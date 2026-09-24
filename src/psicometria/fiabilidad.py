"""Fiabilidad de las dimensiones y subescalas (consistencia interna).

Implementa Cronbach's alpha, McDonald's omega y el coeficiente de
Spearman-Brown con numpy puro, sin dependencias adicionales. Umbral
profesional de referencia: >= 0.70.

Distinción psicométrica importante (ver reporte): para subescalas de solo
2 ítems (acoso sexual, acoso laboral, doble presencia, condiciones del
trabajo y salud auto percibida en el instrumento oficial MDT), el alfa de
Cronbach es inestable por construcción; en esos casos se reporta el
coeficiente de Spearman-Brown y la subescala se marca como "descriptiva,
no psicométrica". Nunca se presenta α como si fuera válido en subescalas
de 2 ítems sin esta distinción.
"""
import numpy as np
import pandas as pd


def cronbach_alpha(df_items: pd.DataFrame) -> float:
    """Calcula Cronbach's alpha (consistencia interna).

    alpha = (k / (k - 1)) * (1 - (sum var_i / var_total))

    Válido solo para subescalas de 3+ ítems. Con 2 ítems usar
    spearman_brown() (el alpha es inestable por construcción).

    Args:
        df_items: DataFrame con columnas = ítems de una subescala.

    Returns:
        alpha en [0, 1]. 1 = correlación perfecta entre ítems.
    """
    k = df_items.shape[1]
    if k < 2:
        return float("nan")
    var_items = df_items.var(axis=0, ddof=1)
    var_total = df_items.sum(axis=1).var(ddof=1)
    if var_total == 0:
        return float("nan")
    alpha = (k / (k - 1)) * (1 - (var_items.sum() / var_total))
    return float(alpha)


def _cargas_1_factor(df_items: pd.DataFrame) -> np.ndarray:
    """Cargas factoriales de un modelo de un factor vía análisis de componentes.

    Usa la descomposición de la matriz de correlaciones (eigendecomposition).
    Retorna las cargas estandarizadas lambda para cada ítem.

    Retorna un arreglo de NaN si no hay suficientes filas, hay valores NaN en
    la correlación (varianza nula) o la descomposición no converge.
    """
    if df_items.shape[0] < 2:
        return np.full(df_items.shape[1], np.nan)
    corr = np.corrcoef(df_items.to_numpy(dtype=float).T)
    if not np.isfinite(corr).all():
        return np.full(df_items.shape[1], np.nan)
    try:
        eigvals, eigvecs = np.linalg.eigh(corr)
    except np.linalg.LinAlgError:
        return np.full(df_items.shape[1], np.nan)
    idx = int(np.argmax(eigvals))
    cargas = eigvecs[:, idx] * np.sqrt(eigvals[idx])
    return cargas


def mcdonald_omega(df_items: pd.DataFrame) -> float:
    """Calcula McDonald's omega (fiabilidad del modelo congeneric unifactorial).

    omega = (sum lambda)^2 / [(sum lambda)^2 + sum(1 - lambda^2)]

    Es más robusto que alpha porque no asume tau-equivalencia.

    Retorna NaN si los datos no permiten calcular las cargas (menos de 2 filas,
    varianza nula, o descomposición no convergente).
    """
    if df_items.shape[1] < 2:
        return float("nan")
    lambdas = _cargas_1_factor(df_items)
    if not np.isfinite(lambdas).all():
        return float("nan")
    numerador = np.sum(lambdas) ** 2
    denominador = numerador + np.sum(1 - lambdas**2)
    if denominador == 0:
        return float("nan")
    return float(numerador / denominador)


def spearman_brown(df_items: pd.DataFrame) -> float:
    """Coeficiente de Spearman-Brown para subescalas de 2 ítems.

    SB = 2r / (1 + r), con r = correlación de Pearson entre los 2 ítems.
    Es el estimador recomendado cuando la subescala tiene solo 2 ítems:
    el alfa de Cronbach es inestable por construcción en ese caso.

    Args:
        df_items: DataFrame con exactamente 2 columnas (ítems de la subescala).

    Returns:
        SB en [0, 1], o NaN si no es calculable (menos de 2 filas,
        número de ítems distinto de 2, varianza nula o r = -1).
    """
    if df_items.shape[1] != 2 or df_items.shape[0] < 2:
        return float("nan")
    with np.errstate(all="ignore"):
        corr = np.corrcoef(df_items.to_numpy(dtype=float).T)
    if not np.isfinite(corr).all():
        return float("nan")
    r = float(corr[0, 1])
    if 1 + r == 0:
        return float("nan")
    return float(2 * r / (1 + r))


def clasificar_subescala(n_items: int) -> str:
    """Clasifica una subescala según su número de ítems.

    Returns:
        'psicometrica': 3+ ítems; α/ω son reportables.
        'descriptiva_no_psicometrica': 2 ítems; reportar Spearman-Brown o
            solo descriptivo (el alfa es inestable ahí).
        'no_evaluable': 0-1 ítems.
    """
    if n_items >= 3:
        return "psicometrica"
    if n_items == 2:
        return "descriptiva_no_psicometrica"
    return "no_evaluable"