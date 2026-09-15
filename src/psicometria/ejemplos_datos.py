"""Generador de datos sintéticos de ejemplo.

Genera respuestas con una estructura de 2 factores conocida (demandas y
recursos) para demostrar el pipeline psicométrico sin necesidad de datos
reales. La intención de rotación se genera dependiente de los factores
(+demandas, -recursos), según la dirección que predice el modelo JD-R.
"""
import numpy as np
import pandas as pd

from .instrumento import ITEMS, items_de_dimension


def generar_datos_ejemplo(n: int = 300, semilla: int = 42) -> pd.DataFrame:
    """Genera un DataFrame sintético de respuestas tipo Likert (1-5).

    Args:
        n: Número de filas (respondientes).
        semilla: Semilla para reproducibilidad.

    Returns:
        DataFrame con columnas = ids de ítems (valores 1-5, un decimal)
        y una columna binaria 'intencion_rotacion'.
    """
    rng = np.random.default_rng(semilla)

    # Factores latentes independientes (demandas y recursos)
    z_dem = rng.normal(0, 1, n)
    z_rec = rng.normal(0, 1, n)

    cargas = 0.8
    ruido = np.sqrt(1 - cargas**2)

    datos = {}
    for iid, meta in ITEMS.items():
        z = z_dem if meta["dimension"] == "demandas" else z_rec
        valor = 3.0 + 1.5 * (cargas * z + ruido * rng.normal(0, 1, n))
        datos[iid] = np.round(np.clip(valor, 1, 5), 1)

    df = pd.DataFrame(datos)

    # Intención de rotación: +demandas, -recursos (+ ruido)
    logit = -0.5 + 0.8 * z_dem - 0.8 * z_rec + rng.normal(0, 0.5, n)
    p = 1.0 / (1.0 + np.exp(-logit))
    df["intencion_rotacion"] = (rng.uniform(0, 1, n) < p).astype(int)

    return df