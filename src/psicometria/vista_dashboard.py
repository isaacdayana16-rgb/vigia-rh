"""Vista del dashboard para la vía psicométrica validada.

Muestra los perfiles psicosociales (demandas y recursos por separado)
junto con indicadores de fiabilidad y validez. Es completamente aditiva:
cualquier error interno solo afecta a esta sección y no rompe el dashboard.
"""
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path.cwd()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.psicometria.instrumento import ITEMS, items_de_dimension
from src.psicometria.puntuaciones import calcular_puntuaciones
from src.psicometria.fiabilidad import cronbach_alpha, mcdonald_omega
from src.psicometria.validacion import analisis_factorial, regresion_logistica
from src.psicometria.ejemplos_datos import generar_datos_ejemplo
from src.utils.logger import logger


def _cargar_datos_encuesta(project_root) -> tuple:
    """Carga respuestas desde data/encuestas/ o genera datos de demostración.

    Returns:
        (df, es_demo): DataFrame de respuestas y flag si son datos sintéticos.
    """
    encuestas_dir = Path(project_root) / "data" / "encuestas"
    if encuestas_dir.exists():
        archivos = sorted(encuestas_dir.glob("*.csv"))
        if archivos:
            df = pd.read_csv(archivos[0])
            return df, False
    return generar_datos_ejemplo(n=200, semilla=42), True


def componente_perfiles_psicosociales(project_root) -> None:
    """Renderiza la sección de perfiles psicosociales validados (COPSOQ).

    Args:
        project_root: Ruta raíz del proyecto.
    """
    try:
        import streamlit as st
        import plotly.express as px

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

        st.warning(
            "⚠️ *Aviso ético:* Esta vía mide constructos psicosociales a nivel grupal. "
            "No es diagnóstico clínico ni debe usarse para decisiones individuales "
            "de contratación, despido, ascenso o sanción.*"
        )

        logger.info("Sección de perfiles psicosociales renderizada")
    except Exception as e:
        try:
            import streamlit as st
            st.error(f"❌ Error en perfiles psicosociales: {e}")
        except Exception:
            pass
        logger.error(f"Error en componente_perfiles_psicosociales: {e}", exc_info=True)