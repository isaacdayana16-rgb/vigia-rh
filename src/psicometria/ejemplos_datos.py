"""Generador de datos sintéticos de ejemplo (instrumento oficial MDT).

Genera respuestas a los 58 ítems del cuestionario oficial del MDT-Ecuador
(escala Likert 1-4) con una estructura latente conocida (factor general de
bienestar + factores específicos por dimensión y subescala) para demostrar
el pipeline psicométrico sin necesidad de datos reales.

La intención de rotación se genera dependiente del bienestar general:
a mayor riesgo percibido (menor puntaje), mayor intención de rotación.
Con la dirección de puntaje oficial (menor puntaje = mayor riesgo), los
coeficientes esperados de las puntuaciones de dimensión frente a la
rotación son NEGATIVOS.

El campo demográfico 'tipo_jornada' (turno fijo/rotativo) se genera con
efecto sobre los ítems que mencionan explícitamente "jornada" (item_04 y
item_28 del Anexo 11.1) y un efecto leve sobre carga y recuperación: los
turnos rotativos correlacionan con mayor riesgo psicosocial, sobre todo en
"jornada de trabajo" (Aguilar Ortega & Vega Cauich, 2024, n=597). Es un
efecto simulado para demostración, no una relación causal verificada.
"""
import numpy as np
import pandas as pd

from .instrumento import ITEMS, DIMENSIONES, SUBESCALAS_OTROS, items_de_dimension, items_de_subescala

# Ítems con mención explícita de "jornada" en el Anexo 11.1 del PDF oficial
ITEMS_JORNADA = ["item_04", "item_28"]

# Dimensiones sobre las que el turno rotativo ejerce efecto leve
DIMENSIONES_EFECTO_JORNADA = ["carga_ritmo_trabajo", "recuperacion"]

_PROVINCIAS = [
    ("PICHINCHA", "QUITO"),
    ("GUAYAS", "GUAYAQUIL"),
    ("AZUAY", "CUENCA"),
    ("EL ORO", "MACHALA"),
    ("TUNGURAHUA", "AMBATO"),
    ("MANABI", "PORTOVIEJO"),
    ("LOJA", "LOJA"),
    ("IMBABURA", "IBARRA"),
]


def generar_datos_ejemplo(n: int = 300, semilla: int = 42) -> pd.DataFrame:
    """Genera un DataFrame sintético de respuestas al instrumento MDT (1-4).

    Args:
        n: Número de filas (respondientes).
        semilla: Semilla para reproducibilidad.

    Returns:
        DataFrame con columnas = datos generales (A-I del Anexo 11.1 +
        tipo_jornada), ids de ítems item_01..item_58 (valores 1-4) y una
        columna binaria 'intencion_rotacion'.
    """
    rng = np.random.default_rng(semilla)

    # Factor general de bienestar + factores específicos por dimensión
    z_gral = rng.normal(0, 1, n)
    z_dim = {}
    for dim in DIMENSIONES:
        z_dim[dim] = 0.7 * z_gral + np.sqrt(1 - 0.49) * rng.normal(0, 1, n)

    # Factores específicos de subescala (débilmente correlacionados: en datos
    # reales, los ítems de acoso/doble presencia suelen ser poco consistentes)
    z_sub = {}
    for sub in SUBESCALAS_OTROS:
        z_sub[sub] = 0.5 * z_dim["otros_puntos_importantes"] + np.sqrt(1 - 0.25) * rng.normal(0, 1, n)

    tipo_jornada = rng.choice(["turno_fijo", "turno_rotativo"], size=n, p=[0.55, 0.45])
    es_rotativo = tipo_jornada == "turno_rotativo"

    datos = {}
    for iid, meta in ITEMS.items():
        if meta["subdimension"]:
            z = z_sub[meta["subdimension"]]
            carga = 0.5
        else:
            z = z_dim[meta["dimension"]]
            carga = 0.85
        valor = 2.5 + (carga * z + np.sqrt(1 - carga**2) * rng.normal(0, 1, n))

        # Efecto simulado del turno rotativo (Aguilar Ortega & Vega Cauich, 2024):
        # fuerte en ítems de "jornada de trabajo", leve en carga y recuperación
        efecto = np.zeros(n)
        if meta["dimension"] in DIMENSIONES_EFECTO_JORNADA:
            efecto = efecto - 0.15
        if iid in ITEMS_JORNADA:
            efecto = efecto - 0.5
        datos[iid] = np.round(np.clip(valor + efecto * es_rotativo, 1, 4), 1)

    df = pd.DataFrame(datos)

    # Datos generales oficiales (Anexo 11.1) + tipo_jornada
    df["fecha"] = pd.to_datetime(rng.integers(0, 30, n), unit="D", origin="2026-09-01").strftime("%d/%m/%Y")
    prov_ciudad = [_PROVINCIAS[i] for i in rng.integers(0, len(_PROVINCIAS), n)]
    df["provincia"] = [p for p, _ in prov_ciudad]
    df["ciudad"] = [c for _, c in prov_ciudad]
    df["area_trabajo"] = rng.choice(["Administrativa", "Operativa"], size=n, p=[0.4, 0.6])
    df["nivel_instruccion"] = rng.choice(
        ["Ninguno", "Educación básica", "Educación media", "Bachillerato",
         "Técnico / Tecnológico", "Tercer nivel", "Cuarto nivel", "Otro"],
        size=n,
    )
    df["antiguedad"] = rng.choice(["0-2 años", "3-10 años", "11-20 años", "Igual o superior a 21 años"], size=n)
    df["edad"] = rng.choice(
        ["16-24 años", "25-34 años", "35-43 años", "44-52 años", "Igual o superior a 53 años"], size=n
    )
    df["autoidentificacion_etnica"] = rng.choice(
        ["Indígena", "Mestizo/a", "Montubio/a", "Afro-ecuatoriano", "Blanco/a", "Otro"], size=n
    )
    df["genero"] = rng.choice(["Masculino", "Femenino"], size=n)
    df["tipo_jornada"] = tipo_jornada

    # Intención de rotación: a mayor riesgo (menor z_gral), mayor rotación
    logit = -0.3 - 0.9 * z_gral + rng.normal(0, 0.5, n)
    p = 1.0 / (1.0 + np.exp(-logit))
    df["intencion_rotacion"] = (rng.uniform(0, 1, n) < p).astype(int)

    return df
