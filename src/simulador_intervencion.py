"""Simulador de intervención psicosocial informado por evidencia externa.

Combina tres capas de evidencia:
  (a) los datos locales de la encuesta MDT: distribución de riesgo con los
      puntos de corte oficiales (Tablas 3-4 del PDF del MDT),
  (b) la dirección asociativa local (correlaciones univariadas
      dimensión-rotación) para PRIORIZAR qué dimensión intervenir,
  (c) tamaños de efecto de meta-análisis publicados sobre intervenciones
      organizacionales, no solo el recálculo con el modelo propio.

EVIDENCIA EXTERNA (verificada durante el desarrollo, septiembre 2026):
- Richardson & Rothstein (2008), Journal of Occupational Health Psychology
  13(1), 69-93: meta-análisis de 36 estudios experimentales (55
  intervenciones, N total = 2,847) de manejo de estrés ocupacional. Efecto
  medio ponderado global d = 0.526 (IC 95%: 0.364-0.687), "efecto medio a
  grande". Las intervenciones cognitivo-conductuales producen los mayores
  efectos. Abstract verificado en Medline (PMID 18211170) y APA PsycNet.
- LaMontagne et al. (2007), American Journal of Health Promotion 21(6):
  revisión sistemática: las intervenciones a nivel ORGANIZACIONAL producen
  mejoras más pequeñas pero más sostenibles que las individuales (hallazgo
  cualitativo de la revisión; sin d único desagregado por contenido).
- Menú de intervenciones HSE/OMS citado en la propia guía oficial del MDT
  (págs. 18-20): carga razonable de trabajo, fomentar trabajo en equipo,
  control y monitoreo de turnos y horas extra, capacitación.
- Mora & Campos (2023, UISEK): brecha documentada en "propuestas de control
  de riesgos" en la literatura ecuatoriana (referencia aportada por el
  solicitante del proyecto; no verificada en línea en esta sesión).

⚠️ DOCUMENTACIÓN HONESTA: esto es una SIMULACIÓN INFORMADA POR EVIDENCIA
EXTERNA, NO una predicción causal verificada:
1. Los tamaños de efecto provienen de contextos poblacionales distintos a la
   muestra local; la transferibilidad no está garantizada.
2. El meta-análisis NO desagrega por contenido de la intervención: se usa el
   d global como aproximación conservadora y el límite superior del IC como
   cota optimista. La desagregación por contenido queda como limitación.
3. La dirección (intervención -> reducción de riesgo) está apoyada por
   estudios experimentales, pero la magnitud exacta para esta población es
   incierta.

No afirma que el modelo "previene accidentes": los resultados se asocian con
indicadores de salud laboral; la relación con accidentabilidad específica es
débil según la evidencia disponible (SUSESO/ISTAS21, Chile: rho -0.29 a -0.34).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path.cwd()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.psicometria.instrumento import (
    DIMENSIONES,
    items_de_dimension,
    clasificar_riesgo_dimension,
    clasificar_riesgo_global,
)
from src.psicometria.puntuaciones import (
    calcular_puntuaciones,
    calcular_suma_global,
)

# Tamaños de efecto del meta-análisis (Richardson & Rothstein, 2008):
# d global 0.526 (aproximación conservadora) y límite superior del IC 95%
# 0.687 (cota optimista). El meta-análisis no desagrega por contenido.
D_CONSERVADOR = 0.526
D_OPTIMISTA = 0.687

INTERVENCIONES = {
    "rediseño_carga_laboral": {
        "descripcion": "Carga razonable de trabajo (HSE: 'asegurar que exista una carga razonable'; OMS: rediseño de la carga laboral)",
        "dimensiones": ["carga_ritmo_trabajo", "organizacion_trabajo"],
    },
    "apoyo_social_y_liderazgo": {
        "descripcion": "Fomentar trabajo en equipo y comunicación efectiva de jefes (HSE; OMS: 'apoyo de jefes mediante comunicación efectiva')",
        "dimensiones": ["liderazgo", "soporte_apoyo"],
    },
    "monitoreo_turnos_horas_extra": {
        "descripcion": "Controlar y monitorear el trabajo por turnos y horas extra (HSE)",
        "dimensiones": ["recuperacion"],
        "nota": "Turnos rotativos correlacionan con mayor riesgo, sobre todo en 'jornada de trabajo' (Aguilar Ortega & Vega Cauich, 2024, n=597).",
    },
    "capacitacion_desarrollo": {
        "descripcion": "Capacitación adecuada a trabajadores, supervisores y jefes (HSE)",
        "dimensiones": ["desarrollo_competencias"],
    },
}


def _distribucion(serie_niveles: pd.Series) -> dict:
    """Cuenta respondientes por nivel de riesgo."""
    clasificados = serie_niveles.dropna()
    return {
        nivel: int((clasificados == nivel).sum())
        for nivel in ("Bajo", "Medio", "Alto")
    }


def priorizar_dimensiones(df: pd.DataFrame) -> dict:
    """Prioriza dimensiones por asociación local con la rotación.

    Usa las correlaciones univariadas (estables frente a la multicolinealidad
    entre dimensiones). Si no hay outcome, todas las dimensiones quedan con
    prioridad nula (no se puede priorizar).

    Returns:
        dict {dimension: correlación con la rotación} (NaN sin outcome).
    """
    punt_norm = calcular_puntuaciones(df, normalizar=True)
    if "intencion_rotacion" not in df.columns:
        return {dim: float("nan") for dim in DIMENSIONES}
    y = df["intencion_rotacion"].to_numpy()
    prioridad = {}
    for dim in DIMENSIONES:
        if dim not in punt_norm.columns or punt_norm[dim].isna().all():
            prioridad[dim] = float("nan")
            continue
        r = np.corrcoef(punt_norm[dim], y)[0, 1]
        prioridad[dim] = float(r) if np.isfinite(r) else float("nan")
    return prioridad


def simular_intervencion(df: pd.DataFrame, intervenciones: list = None) -> dict:
    """Simula el efecto esperado de intervenciones organizacionales.

    Para cada intervención:
      1. Dimensiones afectadas presentes en los datos.
      2. Δ en unidades de SD local: Δsuma = d × σ(dimensión normalizada) × nº ítems.
      3. Recalcula la clasificación oficial de riesgo y cuenta movimientos
         (cuántos salen de Alto y de Medio con el d conservador y el optimista).

    Args:
        df: DataFrame de respuestas (ítems MDT; opcionalmente outcome).
        intervenciones: Lista de claves de INTERVENCIONES a simular
            (default: todas).

    Returns:
        dict con 'intervenciones' (resultados por intervención),
        'prioridad' (correlaciones locales), 'caveats' (limitaciones honestas).
    """
    if intervenciones is None:
        intervenciones = list(INTERVENCIONES)

    punt = calcular_puntuaciones(df)
    punt_norm = calcular_puntuaciones(df, normalizar=True)
    prioridad = priorizar_dimensiones(df)

    resultados = {}
    for nombre in intervenciones:
        if nombre not in INTERVENCIONES:
            raise ValueError(f"Intervención desconocida: {nombre}. Opciones: {list(INTERVENCIONES)}")
        conf = INTERVENCIONES[nombre]
        dims = [d for d in conf["dimensiones"] if d in punt.columns and punt[d].notna().any()]
        if not dims:
            resultados[nombre] = {"viable": False, "motivo": "sin datos de las dimensiones afectadas"}
            continue

        detalle_dims = {}
        for dim in dims:
            n_items = len(items_de_dimension(dim))
            sigma = float(punt_norm[dim].std(ddof=1))
            delta_suma = {
                "conservador": D_CONSERVADOR * sigma * n_items,
                "optimista": D_OPTIMISTA * sigma * n_items,
            }
            antes = _distribucion(punt[dim].apply(lambda s: clasificar_riesgo_dimension(dim, s)))
            despues = {}
            for escenario, ds in delta_suma.items():
                nuevas = punt[dim] + ds
                despues[escenario] = _distribucion(nuevas.apply(lambda s: clasificar_riesgo_dimension(dim, s)))
            detalle_dims[dim] = {
                "n_items": n_items,
                "sigma_local": sigma,
                "delta_suma": delta_suma,
                "riesgo_antes": antes,
                "riesgo_despues": despues,
                "prioridad_correlacion": prioridad.get(dim, float("nan")),
                "salen_de_alto": {
                    "conservador": antes["Alto"] - despues["conservador"]["Alto"],
                    "optimista": antes["Alto"] - despues["optimista"]["Alto"],
                },
            }

        resultados[nombre] = {
            "viable": True,
            "descripcion": conf["descripcion"],
            "fuente_d": "Richardson & Rothstein (2008): d global 0.526 (IC 95% 0.364-0.687); cognitivo-conductuales los mayores efectos",
            "dimensiones": detalle_dims,
            **({"nota": conf["nota"]} if "nota" in conf else {}),
        }

    # Efecto global (solo si las 4 intervenciones son viables y simultáneas)
    suma_global = calcular_suma_global(df)
    efectos_simultaneos = None
    if suma_global is not None and suma_global.notna().any():
        sigma_global = float(punt_norm[list(DIMENSIONES)].mean(axis=1).std(ddof=1))
        delta_global = {
            "conservador": D_CONSERVADOR * sigma_global * len(DIMENSIONES),
            "optimista": D_OPTIMISTA * sigma_global * len(DIMENSIONES),
        }
        antes_g = _distribucion(suma_global.apply(clasificar_riesgo_global))
        despues_g = {}
        for escenario, dg in delta_global.items():
            # aproxima el desplazamiento global sumando los deltas por dimensión
            nuevas = suma_global + dg * len(DIMENSIONES)
            despues_g[escenario] = _distribucion(nuevas.apply(clasificar_riesgo_global))
        efectos_simultaneos = {
            "nota": "Aproximación de las 4 intervenciones simultáneas; el efecto combinado real no es aditivo (limitación).",
            "delta_suma": delta_global,
            "riesgo_antes": antes_g,
            "riesgo_despues": despues_g,
            "salen_de_alto": {
                "conservador": antes_g["Alto"] - despues_g["conservador"]["Alto"],
                "optimista": antes_g["Alto"] - despues_g["optimista"]["Alto"],
            },
        }

    caveats = [
        "Simulación informada por evidencia externa, NO predicción causal verificada.",
        "Los tamaños de efecto provienen de Richardson & Rothstein (2008; 36 estudios, "
        "N=2,847) en contextos distintos a la muestra local; la transferibilidad no está garantizada.",
        "El meta-análisis no desagrega por contenido de la intervención: d global como "
        "aproximación conservadora (0.526) y límite superior del IC como cota optimista (0.687).",
        "Las intervenciones a nivel organizacional producen mejoras más pequeñas pero más "
        "sostenibles que las individuales (LaMontagne et al., 2007); el escenario "
        "conservador es el más apropiado para intervenciones organizacionales.",
        "No afirma que el modelo 'previene accidentes': los resultados se asocian con "
        "indicadores de salud laboral; la relación con accidentabilidad específica es "
        "débil según la evidencia disponible (SUSESO/ISTAS21, Chile: rho -0.29 a -0.34).",
    ]

    return {
        "intervenciones": resultados,
        "prioridad": prioridad,
        "efectos_simultaneos": efectos_simultaneos,
        "caveats": caveats,
    }


def _linea_riesgo(nombre: str, antes: dict, despues: dict, escenario: str) -> str:
    """Formatea una línea de movimiento de riesgo."""
    return (
        f"    {nombre}: Bajo {antes['Bajo']}->{despues[escenario]['Bajo']}  "
        f"Medio {antes['Medio']}->{despues[escenario]['Medio']}  "
        f"Alto {antes['Alto']}->{despues[escenario]['Alto']}"
    )


def generar_reporte_texto(df: pd.DataFrame) -> str:
    """Genera el texto del reporte del simulador de intervención."""
    r = simular_intervencion(df)

    lineas = []
    lineas.append("=" * 64)
    lineas.append("SIMULADOR DE INTERVENCIÓN PSICOSOCIAL — Vigía RH")
    lineas.append("=" * 64)
    lineas.append("Simulación INFORMADA POR EVIDENCIA EXTERNA (no predicción causal)")
    lineas.append("Efectos de referencia: Richardson & Rothstein (2008), d=0.526 (IC 0.364-0.687)")

    lineas.append("\n[1] PRIORIDAD LOCAL (correlación dimensión-rotación)")
    lineas.append("-" * 64)
    for dim, valor in r["prioridad"].items():
        v = f"{valor:+.3f}" if valor == valor else "N/D (sin outcome)"
        lineas.append(f"  {dim:26s}: {v}")

    lineas.append("\n[2] EFECTO ESPERADO POR INTERVENCIÓN (clasificación oficial)")
    lineas.append("-" * 64)
    for nombre, res in r["intervenciones"].items():
        lineas.append(f"  {nombre}:")
        if not res.get("viable"):
            lineas.append(f"    No viable: {res['motivo']}")
            continue
        lineas.append(f"    ({res['descripcion']})")
        for dim, d in res["dimensiones"].items():
            lineas.append(
                f"    {dim}: Δsuma {d['delta_suma']['conservador']:+.1f} a "
                f"{d['delta_suma']['optimista']:+.1f} puntos "
                f"(σ local={d['sigma_local']:.2f}, n={d['n_items']} ítems)"
            )
            lineas.append(_linea_riesgo(f"  escenario conservador", d["riesgo_antes"], d["riesgo_despues"], "conservador"))
            lineas.append(_linea_riesgo(f"  escenario optimista", d["riesgo_antes"], d["riesgo_despues"], "optimista"))
        if "nota" in res:
            lineas.append(f"    Nota: {res['nota']}")

    if r["efectos_simultaneos"]:
        e = r["efectos_simultaneos"]
        lineas.append("\n[3] EFECTO SIMULTÁNEO APROXIMADO (4 intervenciones)")
        lineas.append("-" * 64)
        lineas.append(
            f"  RIESGO GLOBAL: Bajo {e['riesgo_antes']['Bajo']}->{e['riesgo_despues']['conservador']['Bajo']}  "
            f"Medio {e['riesgo_antes']['Medio']}->{e['riesgo_despues']['conservador']['Medio']}  "
            f"Alto {e['riesgo_antes']['Alto']}->{e['riesgo_despues']['conservador']['Alto']}  (conservador)"
        )
        lineas.append(
            f"  RIESGO GLOBAL: Bajo {e['riesgo_antes']['Bajo']}->{e['riesgo_despues']['optimista']['Bajo']}  "
            f"Medio {e['riesgo_antes']['Medio']}->{e['riesgo_despues']['optimista']['Medio']}  "
            f"Alto {e['riesgo_antes']['Alto']}->{e['riesgo_despues']['optimista']['Alto']}  (optimista)"
        )
        lineas.append(f"  ({e['nota']})")

    lineas.append("\n[4] CAUTELAS (documentación honesta)")
    lineas.append("-" * 64)
    for c in r["caveats"]:
        lineas.append(f"  - {c}")

    lineas.append("\n" + "=" * 64)
    lineas.append("[!] AVISO ÉTICO: análisis a nivel grupal; NO diagnóstico clínico;")
    lineas.append("NO para decisiones individuales de contratación, despido, ascenso o sanción.")
    lineas.append("=" * 64)

    return "\n".join(lineas)


def main(argv=None) -> int:
    """Punto de entrada del CLI: `python -m src.simulador_intervencion`."""
    import argparse

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    parser = argparse.ArgumentParser(
        prog="python -m src.simulador_intervencion",
        description="Simulador de intervención psicosocial informado por evidencia externa (MDT).",
    )
    parser.add_argument("archivo", nargs="?", help="Ruta al CSV de respuestas (default: datos de demostración).")
    args = parser.parse_args(argv)

    if args.archivo:
        if not Path(args.archivo).is_file():
            print(f"❌ El archivo no existe: {args.archivo}", file=sys.stderr)
            return 2
        df = pd.read_csv(args.archivo)
    else:
        from src.psicometria.ejemplos_datos import generar_datos_ejemplo
        df = generar_datos_ejemplo(n=200, semilla=42)

    print(generar_reporte_texto(df))
    return 0


if __name__ == "__main__":
    sys.exit(main())
