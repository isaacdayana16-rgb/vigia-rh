"""Simulador de tamaño de muestra vs fiabilidad (α/ω) con el instrumento MDT.

Simula con datos sintéticos del instrumento oficial MDT-Ecuador (58 ítems,
escala 1-4) cómo cambian Cronbach α y McDonald ω según el tamaño de muestra
N. Sirve para fijar el N objetivo de campo con las dimensiones REALES del
instrumento (Paso 1), no con reglas genéricas ni con el instrumento anterior
(COPSOQ de 13 ítems).

Alcance: el N objetivo se fija para las 8 dimensiones principales (4-6 ítems
cada una). Las subescalas de 2 ítems (acoso sexual, acoso laboral, doble
presencia, condiciones del trabajo, salud auto percibida) son inestables a
cualquier N y se reportan como descriptivas (ver fiabilidad.clasificar_subescala).

HALLAZGO DE LA SIMULACIÓN (evidencia, no suposición): la dimensión
"otros_puntos_importantes" es heterogénea por diseño (24 ítems que mezclan
8 subconstructos débilmente correlacionados) y converge a alpha ≈ 0.68 <
0.70 INDEPENDIENTEMENTE de N: el límite es estructural, no de tamaño de
muestra. La propia guía oficial lo anticipa: "Dimensión otros puntos
importantes: constituye el punto de partida para aplicar evaluaciones más
específicas sobre el tema" (pág. 17). Por eso recomendar_n() excluye por
defecto esa dimensión del criterio de peor caso.

Es una simulación pedagógica con datos sintéticos: NO constituye validación
con datos reales ni reemplaza la regla clásica de 10 sujetos por ítem
(Nunnally & Bernstein, 1994) para análisis factorial del instrumento completo.
"""
import numpy as np

from .ejemplos_datos import generar_datos_ejemplo
from .fiabilidad import cronbach_alpha, mcdonald_omega
from .instrumento import DIMENSIONES, items_de_dimension

# Dimensiones excluidas por defecto del criterio de peor caso: la simulación
# muestra que su alfa no alcanza 0.70 a ningún N (heterogeneidad estructural).
DIMENSIONES_HETEROGENEAS = ("otros_puntos_importantes",)


def simular_fiabilidad_n(n: int, semilla: int = 42) -> dict:
    """Calcula α/ω por dimensión principal con N respondientes simulados.

    Args:
        n: Tamaño de muestra simulado.
        semilla: Semilla para reproducibilidad.

    Returns:
        dict {dimension: {n_items, alpha, omega}} para las 8 dimensiones.
    """
    df = generar_datos_ejemplo(n=n, semilla=semilla)
    resultado = {}
    for dimension in DIMENSIONES:
        items = items_de_dimension(dimension)
        resultado[dimension] = {
            "n_items": len(items),
            "alpha": cronbach_alpha(df[items]),
            "omega": mcdonald_omega(df[items]),
        }
    return resultado


def _valores_peor_caso(r: dict, excluir: tuple) -> tuple:
    """Valores (min) de α/ω por criterio en una simulación.

    Returns:
        (valores_excluyendo, valores_todas): listas de α/ω finitos para las
        dimensiones excluyendo `excluir` y para todas las dimensiones.
    """
    vals_excl = [
        m[key]
        for dim, m in r.items()
        if dim not in excluir and m["n_items"] >= 3
        for key in ("alpha", "omega")
        if np.isfinite(m[key])
    ]
    vals_todas = [
        m[key]
        for m in r.values()
        if m["n_items"] >= 3
        for key in ("alpha", "omega")
        if np.isfinite(m[key])
    ]
    return vals_excl, vals_todas


def recomendar_n(
    n_min: int = 50,
    n_max: int = 400,
    paso: int = 10,
    semillas: int = 5,
    umbral: float = 0.70,
    excluir_dimensiones: tuple = DIMENSIONES_HETEROGENEAS,
) -> dict:
    """Busca el N mínimo donde el peor α/ω de las dimensiones ≥ umbral.

    Para cada N (en múltiplos de `paso`) simula con varias semillas y toma la
    mediana del peor caso entre dimensiones principales (>= 3 ítems). Por
    defecto excluye las dimensiones heterogéneas (ver DIMENSIONES_HETEROGENEAS);
    el criterio incluyendo todas las dimensiones se reporta como
    'n_recomendado_todas' para transparencia.

    Args:
        n_min: N inicial de la búsqueda.
        n_max: N final de la búsqueda.
        paso: Incremento de N.
        semillas: Número de semillas por punto (robustez).
        umbral: Umbral de fiabilidad (0.70 convencional).
        excluir_dimensiones: Dimensiones excluidas del criterio de peor caso.

    Returns:
        dict con 'n_recomendado' (int o None si ninguna N alcanza el umbral),
        'n_recomendado_todas', 'tabla' (list de dicts por N), 'umbral',
        'semillas', 'dimensiones_excluidas'.
    """
    tabla = []
    recomendado = None
    recomendado_todas = None
    for n in range(n_min, n_max + 1, paso):
        peores_excl = []
        peores_todas = []
        for s in range(1, semillas + 1):
            r = simular_fiabilidad_n(n, semilla=s)
            vals_excl, vals_todas = _valores_peor_caso(r, excluir_dimensiones)
            if vals_excl:
                peores_excl.append(min(vals_excl))
            if vals_todas:
                peores_todas.append(min(vals_todas))
        mediana_excl = float(np.median(peores_excl)) if peores_excl else float("nan")
        mediana_todas = float(np.median(peores_todas)) if peores_todas else float("nan")
        ok = bool(np.isfinite(mediana_excl) and mediana_excl >= umbral)
        ok_todas = bool(np.isfinite(mediana_todas) and mediana_todas >= umbral)
        if ok and recomendado is None:
            recomendado = n
        if ok_todas and recomendado_todas is None:
            recomendado_todas = n
        tabla.append({
            "n": n,
            "mediana_peor_caso": mediana_excl,
            "mediana_peor_caso_todas": mediana_todas,
            "ok": ok,
            "ok_todas": ok_todas,
        })
    return {
        "n_recomendado": recomendado,
        "n_recomendado_todas": recomendado_todas,
        "tabla": tabla,
        "umbral": umbral,
        "semillas": semillas,
        "dimensiones_excluidas": list(excluir_dimensiones),
    }
