import streamlit as st
import sys
from pathlib import Path

PROJECT_ROOT = Path.cwd()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datos import cargar_datos, agregar_indice_compuesto_jdr
from src.utils.logger import logger
from src.psicometria.vista_dashboard import componente_perfiles_psicosociales
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

# Manejo de errores global para evitar caídas
try:
    # Logging de inicio de sesión
    logger.info("Iniciando dashboard Vigía RH")

    st.title("🔎 Vigía RH — Analítica Predictiva de Rotación")
    st.markdown("Sistema de análisis de riesgo de rotación de personal")

    st.divider()

    # Carga de datos con componente modular
    st.subheader("Cargar archivo de datos")
    df_cargado = componente_carga_archivo()

    if df_cargado is not None:
        df = df_cargado
        logger.info(f"Archivo cargado exitosamente: {len(df)} registros")
    else:
        try:
            df = cargar_datos()
            logger.info(f"Datos default cargados: {len(df)} registros")
        except Exception as e:
            logger.error(f"Error cargando datos default: {e}", exc_info=True)
            st.error("❌ Error crítico cargando datos default. Contacta al administrador.")
            st.stop()

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

    st.divider()

    # Vía psicométrica validada (aditiva; los errores internos no rompen la app)
    componente_perfiles_psicosociales(PROJECT_ROOT)

    # Logging de fin de ejecución
    logger.info("Dashboard renderizado exitosamente")

except Exception as e:
    # Capturar cualquier error no manejado para evitar caída total
    logger.critical(f"Error crítico no manejado en dashboard: {e}", exc_info=True)
    st.error(f"❌ Error crítico: {str(e)}")
    st.info("Por favor recarga la página. Si el problema persiste, contacta al administrador.")