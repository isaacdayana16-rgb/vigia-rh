"""Fiabilidad de las subescalas (consistencia interna).

Implementa Cronbach's alpha y McDonald's omega con numpy puro,
sin dependencias adicionales. Umbral profesional de referencia: >= 0.70.
"""
import numpy as np
import pandas as pd


def cronbach_alpha(df_items: pd.DataFrame) -> float:
    """Calcula Cronbach's alpha (consistencia interna).

    alpha = (k / (k - 1)) * (1 - (sum var_i / var_total))

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
    """
    corr = np.corrcoef(df_items.to_numpy(dtype=float).T)
    eigvals, eigvecs = np.linalg.eigh(corr)
    idx = int(np.argmax(eigvals))
    cargas = eigvecs[:, idx] * np.sqrt(eigvals[idx])
    return cargas


def mcdonald_omega(df_items: pd.DataFrame) -> float:
    """Calcula McDonald's omega (fiabilidad del modelo congeneric unifactorial).

    omega = (sum lambda)^2 / [(sum lambda)^2 + sum(1 - lambda^2)]

    Es más robusto que alpha porque no asume tau-equivalencia.
    """
    if df_items.shape[1] < 2:
        return float("nan")
    lambdas = _cargas_1_factor(df_items)
    numerador = np.sum(lambdas) ** 2
    denominador = numerador + np.sum(1 - lambdas**2)
    if denominador == 0:
        return float("nan")
    return float(numerador / denominador)