"""Vista del dashboard para la vía psicométrica validada.

Muestra los perfiles psicosociales (demandas y recursos por separado)
junto con indicadores de fiabilidad y validez. Es completamente aditiva:
cualquier error interno solo afecta a esta sección y no rompe el dashboard.
"""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

PROJECT_ROOT = Path.cwd()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.psicometria.instrumento import ITEMS, items_de_dimension
from src.psicometria.puntuaciones import calcular_puntuaciones
from src.psicometria.fiabilidad import cronbach_alpha, mcdonald_omega
from src.psicometria.validacion import analisis_factorial, regresion_logistica
from src.psicometria.ejemplos_datos import generar_datos_ejemplo
from src.psicometria.calidad_datos import reporte_calidad_datos
from src.utils.logger import logger


def _metricas_fiabilidad(df) -> dict:
    """Calcula alpha y omega por dimensión (o None si no calculable)."""
    metricas = {}
    for dimension in ["demandas", "recursos"]:
        items = [i for i in items_de_dimension(dimension) if i in df.columns]
        if len(items) >= 2:
            a = cronbach_alpha(df[items])
            o = mcdonald_omega(df[items])
            metricas[dimension] = {
                "alpha": None if not a or a != a else a,
                "omega": None if not o or o != o else o,
            }
    return metricas


def componente_simulador_psicometria() -> None:
    """Simulador interactivo (DEMO): varía el tamaño de muestra y observa α/ω.

    Es una herramienta pedagógica para ilustrar cómo la fiabilidad depende del
    tamaño de muestra. NO constituye validación con datos reales.
    """
    st.markdown("#### 🧪 Simulador de fiabilidad según tamaño de muestra")
    st.caption(
        "**Demo pedagógica:** varía N y observa cómo cambian Cronbach α y McDonald ω. "
        "No es una validación real."
    )
    n = st.slider("Tamaño de muestra (N)", min_value=30, max_value=500, value=150, step=10)
    df_demo = generar_datos_ejemplo(n=n, semilla=42)
    metricas = _metricas_fiabilidad(df_demo)

    col1, col2 = st.columns(2)
    with col1:
        for dimension in ["demandas", "recursos"]:
            if dimension in metricas:
                a = metricas[dimension]["alpha"]
                st.metric(
                    f"α {dimension.capitalize()} (N={n})",
                    f"{a:.3f}" if a is not None else "N/D",
                )
    with col2:
        for dimension in ["demandas", "recursos"]:
            if dimension in metricas:
                o = metricas[dimension]["omega"]
                st.metric(
                    f"ω {dimension.capitalize()} (N={n})",
                    f"{o:.3f}" if o is not None else "N/D",
                )

    st.caption(
        "Observa: con N pequeño, α/ω pueden ser inestables; estabilizan al crecer N. "
        "Esto fundamenta la recomendación de ≥150 respondientes."
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
                continue  # archivo ilegible: pasar al siguiente
            if df.empty:
                continue  # sin filas de datos
            if any(iid in df.columns for iid in ITEMS):
                return df, False
    return generar_datos_ejemplo(n=200, semilla=42), True


def componente_perfiles_psicosociales(project_root) -> None:
    """Renderiza la sección de perfiles psicosociales validados (COPSOQ).

    Args:
        project_root: Ruta raíz del proyecto.
    """
    try:
        st.subheader("🧬 Perfiles psicosociales (vía validada — COPSOQ)")
        st.caption(
            "Mide Job Demands y Job Resources por separado con un instrumento "
            "basado en COPSOQ-ISTAS21. NO es un índice único, es un perfil dimensional."
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

        # Fiabilidad por dimensión
        col1, col2 = st.columns(2)
        with col1:
            for dimension in ["demandas", "recursos"]:
                items = [i for i in items_de_dimension(dimension) if i in df.columns]
                if len(items) >= 2:
                    a = cronbach_alpha(df[items])
                    o = mcdonald_omega(df[items])
                    st.metric(
                        f"Fiabilidad — {dimension.capitalize()}",
                        f"α={a:.2f} · ω={o:.2f}",
                    )

        # Perfil medio de demandas vs recursos
        perfil = punt[["demandas", "recursos"]].mean().rename_axis("Dimensión").reset_index()
        perfil.columns = ["Dimensión", "Puntuación"]
        fig = px.bar(
            perfil,
            x="Dimensión",
            y="Puntuación",
            range_y=[1, 5],
            title="Perfil psicosocial promedio (escala 1-5)",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Validez de constructo (estructura factorial)
        st.markdown("**Validez de constructo (análisis factorial):**")
        if len(ids_items) >= 2:
            cargas, varianza = analisis_factorial(df[ids_items], n_factores=2)
            st.dataframe(cargas.round(3))
            st.caption(f"Varianza explicada: " + ", ".join(
                f"F{i + 1}={v:.2%}" for i, v in enumerate(varianza)
            ))

        # Validez de criterio (regresión sobre intención de rotación)
        if "intencion_rotacion" in df.columns:
            X = punt[["demandas", "recursos"]]
            y = df["intencion_rotacion"].to_numpy()
            res = regresion_logistica(X, y)
            coef = res["coeficientes"]
            st.markdown("**Validez de criterio (regresión sobre intención de rotación):**")
            st.write(f"- Demandas: `{coef['demandas']:+.3f}` (signo esperado: +)")
            st.write(f"- Recursos: `{coef['recursos']:+.3f}` (signo esperado: −)")
            direccion_ok = coef["demandas"] > 0 and coef["recursos"] < 0
            if direccion_ok:
                st.success(
                    "Dirección consistente con el modelo JD-R: más demandas → mayor "
                    "rotación; más recursos → menor rotación."
                )
            else:
                st.warning(
                    "La dirección de los coeficientes no coincide con el modelo JD-R. "
                    "Revisa la calidad de los datos."
                )

        # Simulador pedagógico (solo para datos de demostración)
        if es_demo:
            componente_simulador_psicometria()

        st.warning(
            "⚠️ *Aviso ético:* Esta vía mide constructos psicosociales a nivel grupal. "
            "No es diagnóstico clínico ni debe usarse para decisiones individuales "
            "de contratación, despido, ascenso o sanción.*"
        )

        logger.info("Sección de perfiles psicosociales renderizada")
    except Exception as e:
        try:
            st.error(f"❌ Error en perfiles psicosociales: {e}")
        except Exception:
            pass
        logger.error(f"Error en componente_perfiles_psicosociales: {e}", exc_info=True)