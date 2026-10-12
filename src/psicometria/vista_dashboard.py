"""Vista del dashboard para la vía psicométrica validada (instrumento MDT).

Muestra los perfiles psicosociales (8 dimensiones + subescalas del cuestionario
oficial del MDT-Ecuador) junto con indicadores de fiabilidad (α/ω; Spearman-
Brown para subescalas de 2 ítems), clasificación de riesgo con los puntos de
corte oficiales y validez. Es completamente aditiva: cualquier error interno
solo afecta a esta sección y no rompe el dashboard.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

PROJECT_ROOT = Path.cwd()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.psicometria.instrumento import (
    ITEMS,
    DIMENSIONES,
    SUBESCALAS_OTROS,
    items_de_dimension,
    items_de_subescala,
    clasificar_riesgo_dimension,
    clasificar_riesgo_global,
)
from src.psicometria.puntuaciones import (
    calcular_puntuaciones,
    calcular_puntuaciones_subescala,
    calcular_suma_global,
)
from src.psicometria.fiabilidad import (
    cronbach_alpha,
    mcdonald_omega,
    spearman_brown,
    clasificar_subescala,
)
from src.psicometria.validacion import analisis_factorial, regresion_logistica
from src.psicometria.ejemplos_datos import generar_datos_ejemplo
from src.psicometria.calidad_datos import reporte_calidad_datos
from src.psicometria.reporte import N_OBJETIVO_SIMULACION, _distribucion_riesgo
from src.utils.logger import logger

INDICADOR_SALUD_LABORAL = (
    "Los resultados se asocian con indicadores de salud laboral; la relación "
    "con accidentabilidad específica es débil según evidencia disponible "
    "(SUSESO/ISTAS21, Chile: rho -0.29 a -0.34)."
)


def _metricas_fiabilidad(df) -> dict:
    """Calcula α/ω (o Spearman-Brown si 2 ítems) por dimensión y subescala."""
    metricas = {}
    for dimension in DIMENSIONES:
        items = [i for i in items_de_dimension(dimension) if i in df.columns]
        if len(items) >= 2:
            a = cronbach_alpha(df[items])
            o = mcdonald_omega(df[items])
            metricas[dimension] = {
                "alpha": None if not a or a != a else a,
                "omega": None if not o or o != o else o,
                "sb": None,
                "tipo": clasificar_subescala(len(items)),
            }
    for subescala in SUBESCALAS_OTROS:
        items = [i for i in items_de_subescala(subescala) if i in df.columns]
        if len(items) >= 2:
            tipo = clasificar_subescala(len(items))
            if tipo == "descriptiva_no_psicometrica":
                sb = spearman_brown(df[items])
                metricas[subescala] = {
                    "alpha": None,
                    "omega": None,
                    "sb": None if not sb or sb != sb else sb,
                    "tipo": tipo,
                }
            else:
                a = cronbach_alpha(df[items])
                o = mcdonald_omega(df[items])
                metricas[subescala] = {
                    "alpha": None if not a or a != a else a,
                    "omega": None if not o or o != o else o,
                    "sb": None,
                    "tipo": tipo,
                }
    return metricas


def componente_simulador_psicometria() -> None:
    """Simulador interactivo (DEMO): varía el tamaño de muestra y observa α/ω.

    Es una herramienta pedagógica para ilustrar cómo la fiabilidad depende del
    tamaño de muestra (con las dimensiones reales del instrumento MDT). NO
    constituye validación con datos reales.
    """
    st.markdown("#### 🧪 Simulador de fiabilidad según tamaño de muestra")
    st.caption(
        "**Demo pedagógica:** varía N y observa cómo cambian Cronbach α y McDonald ω "
        "con las dimensiones del instrumento MDT. No es una validación real."
    )
    n = st.slider("Tamaño de muestra (N)", min_value=30, max_value=500, value=150, step=10)
    df_demo = generar_datos_ejemplo(n=n, semilla=42)
    metricas = _metricas_fiabilidad(df_demo)

    dimensiones_mostrar = list(DIMENSIONES)
    col1, col2 = st.columns(2)
    with col1:
        for dimension in dimensiones_mostrar:
            if dimension in metricas:
                a = metricas[dimension]["alpha"]
                st.metric(
                    f"α {dimension.replace('_', ' ')} (N={n})",
                    f"{a:.3f}" if a is not None else "N/D",
                )
    with col2:
        for dimension in dimensiones_mostrar:
            if dimension in metricas:
                o = metricas[dimension]["omega"]
                st.metric(
                    f"ω {dimension.replace('_', ' ')} (N={n})",
                    f"{o:.3f}" if o is not None else "N/D",
                )

    st.caption(
        "Observa: la fiabilidad de las dimensiones principales (4-6 ítems) es estable "
        f"desde N pequeño; el N objetivo para análisis indicativo es ≥{N_OBJETIVO_SIMULACION}. "
        "Las subescalas de 2 ítems son inestables a cualquier N y se reportan como "
        "descriptivas (no psicométricas)."
    )


def _cargar_datos_encuesta(project_root) -> tuple:
    """Carga respuestas desde data/encuestas/ o genera datos de demostración.

    Ignora la plantilla vacía y cualquier archivo sin filas de datos reales.

    Returns:
        (df, es_demo): DataFrame de respuestas y flag si son datos sintéticos.
    """
    encuestas_dir = Path(project_root) / "data" / "encuestas"
    plantilla = "plantilla_respuestas.csv"
    if encuestas_dir.exists():
        for archivo in sorted(encuestas_dir.glob("*.csv")):
            if archivo.name == plantilla:
                continue  # la plantilla solo contiene encabezados
            try:
                df = pd.read_csv(archivo)
            except Exception:
                logger.warning(f"Encuesta ilegible, se omite: {archivo.name}")
                continue  # archivo ilegible: pasar al siguiente
            if df.empty:
                continue  # sin filas de datos
            if any(iid in df.columns for iid in ITEMS):
                return df, False
    return generar_datos_ejemplo(n=200, semilla=42), True


def _tabla_riesgo_oficial(df, punt, punt_sub, suma_global) -> pd.DataFrame:
    """Construye la tabla de distribución de riesgo con puntos de corte oficiales."""
    filas = []
    for dimension in DIMENSIONES:
        if dimension not in punt.columns:
            continue
        niveles = punt[dimension].apply(lambda s: clasificar_riesgo_dimension(dimension, s))
        dist = _distribucion_riesgo(niveles)
        filas.append({
            "Escala": dimension.replace("_", " "),
            "Riesgo Bajo": f"{dist['Bajo']['n']} ({dist['Bajo']['pct']:.0%})" if dist["Bajo"]["pct"] is not None else "N/D",
            "Riesgo Medio": f"{dist['Medio']['n']} ({dist['Medio']['pct']:.0%})" if dist["Medio"]["pct"] is not None else "N/D",
            "Riesgo Alto": f"{dist['Alto']['n']} ({dist['Alto']['pct']:.0%})" if dist["Alto"]["pct"] is not None else "N/D",
        })
    for subescala in SUBESCALAS_OTROS:
        if subescala not in punt_sub.columns:
            continue
        niveles = punt_sub[subescala].apply(lambda s: clasificar_riesgo_dimension(subescala, s))
        dist = _distribucion_riesgo(niveles)
        filas.append({
            "Escala": f"↳ {subescala.replace('_', ' ')}",
            "Riesgo Bajo": f"{dist['Bajo']['n']} ({dist['Bajo']['pct']:.0%})" if dist["Bajo"]["pct"] is not None else "N/D",
            "Riesgo Medio": f"{dist['Medio']['n']} ({dist['Medio']['pct']:.0%})" if dist["Medio"]["pct"] is not None else "N/D",
            "Riesgo Alto": f"{dist['Alto']['n']} ({dist['Alto']['pct']:.0%})" if dist["Alto"]["pct"] is not None else "N/D",
        })
    if suma_global is not None and suma_global.notna().any():
        dist_g = _distribucion_riesgo(suma_global.apply(clasificar_riesgo_global))
        filas.append({
            "Escala": "RIESGO GLOBAL (58 ítems)",
            "Riesgo Bajo": f"{dist_g['Bajo']['n']} ({dist_g['Bajo']['pct']:.0%})" if dist_g["Bajo"]["pct"] is not None else "N/D",
            "Riesgo Medio": f"{dist_g['Medio']['n']} ({dist_g['Medio']['pct']:.0%})" if dist_g["Medio"]["pct"] is not None else "N/D",
            "Riesgo Alto": f"{dist_g['Alto']['n']} ({dist_g['Alto']['pct']:.0%})" if dist_g["Alto"]["pct"] is not None else "N/D",
        })
    return pd.DataFrame(filas)


def componente_simulador_intervencion(df) -> None:
    """Simulador de intervención como escenario hipotético basado en la literatura (d = 0.526)."""
    try:
        from src.simulador_intervencion import simular_intervencion
        st.markdown("#### 🛠️ Simulador de intervención psicosocial")
        st.caption(
            "**Escenario hipotético basado en un tamaño de efecto de la literatura (d = 0.526)** "
            "(meta-análisis de Richardson & Rothstein, 2008). No constituye predicción causal ni "
            "proyección garantizada; ilustra variaciones potenciales de riesgo bajo supuestos de la literatura."
        )
        r = simular_intervencion(df)
        filas = []
        for nombre, res in r["intervenciones"].items():
            if res.get("viable"):
                for dim, d in res["dimensiones"].items():
                    filas.append({
                        "Intervención": nombre.replace("_", " ").capitalize(),
                        "Dimensión": dim.replace("_", " "),
                        "Alto (Base)": d["riesgo_antes"]["Alto"],
                        "Alto (Escenario conservador d=0.526)": d["riesgo_despues"]["conservador"]["Alto"],
                        "Alto (Escenario optimista d=0.687)": d["riesgo_despues"]["optimista"]["Alto"],
                    })
        if filas:
            st.dataframe(pd.DataFrame(filas), use_container_width=True)
    except Exception as e:
        logger.error(f"Error en componente_simulador_intervencion: {e}", exc_info=True)


def componente_perfiles_psicosociales(project_root) -> None:
    """Renderiza la sección de perfiles psicosociales (instrumento oficial MDT).

    Args:
        project_root: Ruta raíz del proyecto.
    """
    try:
        st.subheader("🧬 Perfiles psicosociales (instrumento oficial MDT-Ecuador)")
        st.caption(
            "Cuestionario oficial del Ministerio del Trabajo del Ecuador: 58 ítems, "
            "escala Likert 1-4, clasificación de riesgo con los puntos de corte "
            "oficiales (Tablas 3-4). Menor puntaje = mayor riesgo."
        )

        df, es_demo = _cargar_datos_encuesta(project_root)
        if es_demo:
            st.info(
                "Mostrando **datos sintéticos de demostración**. "
                "Coloca tu encuesta real como CSV en `data/encuestas/` para "
                "usar esta vía con datos válidos."
            )
        else:
            # Control de calidad sobre datos reales
            calidad = reporte_calidad_datos(df)
            if calidad["advertencias"]:
                st.warning("📋 **Control de calidad de datos:**")
                for adv in calidad["advertencias"]:
                    st.markdown(f"- {adv}")

        ids_items = [iid for iid in ITEMS if iid in df.columns]
        if not ids_items:
            st.warning("El archivo de encuesta no contiene ítems del instrumento.")
            return

        punt = calcular_puntuaciones(df[ids_items])
        punt_sub = calcular_puntuaciones_subescala(df[ids_items])
        suma_global = calcular_suma_global(df[ids_items])

        # Clasificación oficial de riesgo (Tablas 3-4)
        st.markdown("**Clasificación de riesgo (puntos de corte oficiales):**")
        st.dataframe(_tabla_riesgo_oficial(df, punt, punt_sub, suma_global), use_container_width=True)

        # Fiabilidad por dimensión y subescala (con distinción psicométrica)
        metricas = _metricas_fiabilidad(df)
        st.markdown("**Fiabilidad (consistencia interna):**")
        col1, col2 = st.columns(2)
        mitad = (len(metricas) + 1) // 2
        for i, (nombre, datos) in enumerate(metricas.items()):
            with col1 if i < mitad else col2:
                if datos["tipo"] == "descriptiva_no_psicometrica":
                    sb = datos["sb"]
                    st.metric(
                        f"↳ {nombre.replace('_', ' ')} (2 ítems)",
                        f"SB={sb:.2f}" if sb is not None else "N/D",
                        help="Subescala de 2 ítems: descriptiva, no psicométrica. "
                             "Se reporta Spearman-Brown, no α (el alfa es inestable ahí).",
                    )
                else:
                    a, o = datos["alpha"], datos["omega"]
                    st.metric(
                        f"{nombre.replace('_', ' ')} ({datos['tipo']})",
                        f"α={a:.2f} · ω={o:.2f}" if a is not None and o is not None else "N/D",
                    )

        # Perfil medio por dimensión (media de ítems, escala 1-4)
        punt_norm = calcular_puntuaciones(df[ids_items], normalizar=True)
        perfil = punt_norm[list(DIMENSIONES)].mean().rename_axis("Dimensión").reset_index()
        perfil.columns = ["Dimensión", "Puntuación"]
        fig = px.bar(
            perfil,
            x="Dimensión",
            y="Puntuación",
            range_y=[1, 4],
            title="Perfil psicosocial promedio (escala 1-4; menor = mayor riesgo)",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Validez de constructo (estructura factorial exploratoria)
        st.markdown("**Validez de constructo (análisis factorial exploratorio):**")
        if len(ids_items) >= 2:
            cargas, varianza = analisis_factorial(df[ids_items], n_factores=2)
            st.dataframe(cargas.round(3))
            st.caption(
                "Varianza explicada: " + ", ".join(
                    f"F{i + 1}={v:.2%}" for i, v in enumerate(varianza)
                )
                + ". El instrumento oficial MDT no postula una estructura "
                "bidimensional; este análisis es exploratorio."
            )

        # Validez de criterio (dirección univariada + modelo multivariado)
        if "intencion_rotacion" in df.columns and not es_demo:
            punt_norm = calcular_puntuaciones(df[ids_items], normalizar=True)
            y = df["intencion_rotacion"].to_numpy()
            st.markdown("**Validez de criterio (dirección univariada):**")
            direccion_ok = True
            for dimension in DIMENSIONES:
                if dimension not in punt_norm.columns or punt_norm[dimension].isna().all():
                    continue
                valor = float(np.corrcoef(punt_norm[dimension], y)[0, 1])
                if not np.isfinite(valor):
                    continue
                st.write(f"- {dimension.replace('_', ' ')}: `r={valor:+.3f}` (signo esperado: −)")
                if valor >= 0:
                    direccion_ok = False
            if direccion_ok:
                st.success(
                    "Dirección consistente con la dirección del puntaje oficial "
                    "(menor puntaje = mayor riesgo): a mayor puntaje por dimensión, "
                    "menor intención de rotación."
                )
            else:
                st.warning(
                    "La dirección de la asociación no coincide con la esperada. "
                    "Revisa la calidad de los datos."
                )

        # Simulador pedagógico (solo para datos de demostración)
        if es_demo:
            componente_simulador_psicometria()

        st.warning(
            "⚠️ *Aviso ético:* Esta vía mide constructos psicosociales a nivel grupal. "
            "No es diagnóstico clínico ni debe usarse para decisiones individuales "
            "de contratación, despido, ascenso o sanción."
        )
        st.caption(f"*Nota de cautela:* {INDICADOR_SALUD_LABORAL}")

        logger.info("Sección de perfiles psicosociales renderizada")
    except Exception as e:
        try:
            st.error(f"❌ Error en perfiles psicosociales: {e}")
        except Exception:
            logger.warning("No se pudo mostrar el error en la UI (st.error falló)")
        logger.error(f"Error en componente_perfiles_psicosociales: {e}", exc_info=True)
