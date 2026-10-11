import streamlit as st
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datos import cargar_datos, agregar_indice_compuesto_jdr
from src.utils.logger import logger
from src.psicometria.vista_dashboard import (
    componente_perfiles_psicosociales,
    componente_simulador_intervencion,
    _cargar_datos_encuesta,
)
from src.dashboard.ui_components import (
    componente_carga_archivo,
    componente_metricas_principales,
    componente_filtro_departamento,
    componente_graficas_rotacion,
    componente_indice_jdr,
    componente_explicabilidad_shap,
    componente_modelo_prediccion
)

st.set_page_config(page_title="Vigía RH", layout="wide")


@st.cache_data
def _cargar_datos_encuesta_cacheado(project_root_str):
    """Carga (y cachea) el DataFrame de encuestas para la pestaña del simulador."""
    return _cargar_datos_encuesta(Path(project_root_str))

# Manejo de errores global para evitar caídas
try:
    # Logging de inicio de sesión
    logger.info("Iniciando dashboard Vigía RH")

    st.title("🔎 Vigía RH — Riesgo Psicosocial Laboral")
    st.markdown(
        "Evaluación psicométrica del riesgo psicosocial (MDT-Ecuador, 58 ítems) "
        "con un módulo demostrativo secundario de rotación"
    )

    tab_inicio, tab_psicosocial, tab_simulador, tab_rotacion = st.tabs(
        ["🏠 Inicio", "🧠 Riesgo psicosocial", "🛠️ Simulador (escenario hipotético)", "🧪 Módulo demostrativo (rotación — IBM HR)"]
    )

    with tab_inicio:
        st.subheader("¿Qué es Vigía RH?")
        st.markdown(
            "Vigía RH es una herramienta de People Analytics con dos vías:\n\n"
            "1. **Riesgo psicosocial laboral** (vista principal): evaluación psicométrica "
            "grupal con el Cuestionario de Evaluación de Riesgo Psicosocial del Ministerio "
            "del Trabajo del Ecuador (MDT): 58 ítems, escala Likert 1-4, puntos de corte "
            "oficiales (Tablas 3-4).\n"
            "2. **Módulo demostrativo de rotación** (vista secundaria): pipeline de "
            "analítica entrenado con un dataset público (IBM HR Analytics)."
        )

        st.subheader("Aviso ético")
        st.warning(
            "⚠️ Herramienta **no certificada** y **sin fines de diagnóstico individual** "
            "ni clínico. Los resultados se interpretan a nivel **grupal**; los grupos con "
            "menos de 5 personas se protegen y no se desglosan. No debe usarse para "
            "decisiones individuales de contratación, despido, ascenso o sanción."
        )

        st.subheader("Limitaciones")
        st.info(
            "📋 La **validación psicométrica del instrumento está pendiente de datos de "
            "campo**. El modelo predictivo del módulo demostrativo está **entrenado con un "
            "dataset público (IBM HR Analytics)**, por lo que sus resultados son "
            "ilustrativos y no representan a ninguna organización. Esta herramienta no "
            "sustituye la guía oficial del MDT ni el criterio de profesionales competentes."
        )
        st.caption(
            "Marco ético completo: [docs/CONSENTIMIENTO.md](docs/CONSENTIMIENTO.md) · "
            "[docs/PROTOCOLO_SITUACIONES_DETECTADAS.md](docs/PROTOCOLO_SITUACIONES_DETECTADAS.md)"
        )

    with tab_psicosocial:
        # Vía psicométrica (los errores internos no rompen la app)
        componente_perfiles_psicosociales(PROJECT_ROOT)

    with tab_simulador:
        df_sim, es_demo_sim = _cargar_datos_encuesta_cacheado(str(PROJECT_ROOT))
        if es_demo_sim:
            st.info(
                "📋 **Datos sintéticos de demostración**: no hay respuestas reales en "
                "`data/encuestas/respuestas.csv`. El escenario mostrado es ilustrativo."
            )
        componente_simulador_intervencion(df_sim)

    with tab_rotacion:
        st.info(
            "ℹ️ **Módulo demostrativo.** Esta pestaña usa un **dataset público** "
            "(IBM HR Analytics, Kaggle) con fines ilustrativos. **No corresponde a datos "
            "de una empresa ecuatoriana** ni debe interpretarse como evidencia sobre "
            "condiciones laborales locales."
        )

        # Carga de datos con componente modular
        st.subheader("Cargar archivo de datos")
        df_cargado = componente_carga_archivo()

        if df_cargado is not None:
            df = df_cargado
            datos_disponibles = True
            logger.info(f"Archivo cargado exitosamente: {len(df)} registros")
        else:
            try:
                df = cargar_datos()
                datos_disponibles = True
                logger.info(f"Datos default cargados: {len(df)} registros")
            except Exception as e:
                datos_disponibles = False
                logger.error(f"Error cargando datos default: {e}", exc_info=True)
                st.error("❌ No se pudieron cargar los datos de demostración. Las secciones de rotación no están disponibles en esta ejecución.")

        if datos_disponibles:
            # Calcular índice JD-R
            try:
                df = agregar_indice_compuesto_jdr(df)
                logger.info("Índice JD-R calculado exitosamente")
            except Exception as e:
                logger.error(f"Error calculando índice JD-R: {e}", exc_info=True)
                st.error("❌ Error calculando índice JD-R. Los análisis pueden estar incompletos.")

            st.divider()

            # Métricas principales
            componente_metricas_principales(df)

            st.divider()

            # Filtro por departamento
            df_filtrado = componente_filtro_departamento(df)

            # Gráficas de rotación
            componente_graficas_rotacion(df_filtrado)

            st.divider()

            # Índice JD-R
            componente_indice_jdr(df_filtrado)

            st.divider()

            # Explicabilidad SHAP y modelo predictivo
            componente_explicabilidad_shap(PROJECT_ROOT)
            componente_modelo_prediccion(PROJECT_ROOT)

    # Logging de fin de ejecución
    logger.info("Dashboard renderizado exitosamente")

except Exception as e:
    # Capturar cualquier error no manejado para evitar caída total
    logger.critical(f"Error crítico no manejado en dashboard: {e}", exc_info=True)
    st.error(f"❌ Error crítico: {str(e)}")
    st.info("Por favor recarga la página. Si el problema persiste, contacta al administrador.")