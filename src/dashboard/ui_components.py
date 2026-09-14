"""Componentes UI reutilizables para Vigía RH Dashboard.

Modulariza la interfaz de Streamlit para facilitar mantenimiento
y consistencia visual en toda la aplicación.
"""

import streamlit as st
import pandas as pd
from typing import Optional
import tempfile
import os

from src.datos import (
    cargar_datos, 
    detectar_mapeo_propuesto, 
    mostrar_mapeo_propuesto
)
from src.dashboard.error_handler import validar_tamano_archivo, ErrorDatos
from src.utils.logger import logger


def detectar_formato_archivo(nombre_archivo: str) -> str:
    """Detecta el formato de archivo basado en extensión.
    
    Args:
        nombre_archivo: Nombre del archivo
        
    Returns:
        'csv', 'excel', o 'desconocido'
    """
    extension = nombre_archivo.lower().split('.')[-1] if '.' in nombre_archivo else ''
    
    if extension in ['csv']:
        return 'csv'
    elif extension in ['xlsx', 'xls']:
        return 'excel'
    else:
        return 'desconocido'


def leer_archivo_universal(ruta_archivo: str, formato: str) -> pd.DataFrame:
    """Lee archivo usando el motor apropiado según formato.
    
    Args:
        ruta_archivo: Ruta del archivo
        formato: 'csv' o 'excel'
        
    Returns:
        DataFrame con los datos
        
    Raises:
        ErrorDatos: Si hay problemas de lectura
    """
    try:
        if formato == 'csv':
            # Intentar múltiples encodings comunes en corporativo
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    df = pd.read_csv(ruta_archivo, encoding=encoding)
                    logger.info(f"CSV leído exitosamente con encoding: {encoding}")
                    return df
                except UnicodeDecodeError:
                    continue
            # Si todos fallan, intentar sin especificar encoding
            df = pd.read_csv(ruta_archivo)
            logger.info("CSV leído con encoding default")
            return df
            
        elif formato == 'excel':
            # Leer primera hoja con manejo de errores
            df = pd.read_excel(ruta_archivo, engine='openpyxl')
            logger.info("Excel leído exitosamente")
            return df
            
        else:
            raise ErrorDatos(f"Formato no soportado: {formato}")
            
    except Exception as e:
        raise ErrorDatos(f"Error leyendo archivo {formato}: {str(e)}")


def componente_carga_archivo() -> Optional[pd.DataFrame]:
    """Componente reutilizable para carga de archivos híbridos (CSV/Excel) con mapeo.
    
    Returns:
        DataFrame cargado o None si no se cargó archivo
    """
    archivo_cargado = st.file_uploader(
        "Sube tu archivo (CSV, Excel) - opcional, usa datos default si está vacío", 
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=False
    )
    
    if not archivo_cargado:
        return None
    
    ruta_temp = None
    try:
        # Detectar formato del archivo
        formato = detectar_formato_archivo(archivo_cargado.name)
        logger.info(f"Archivo cargado: {archivo_cargado.name}, formato detectado: {formato}")
        
        if formato == 'desconocido':
            raise ErrorDatos(
                f"Formato no soportado: {archivo_cargado.name}. "
                "Por favor usa CSV, XLSX o XLS."
            )
        
        # Determinar extensión para archivo temporal
        extension_temp = ".csv" if formato == 'csv' else ".xlsx"
        
        # Guardar archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension_temp) as tmp:
            tmp.write(archivo_cargado.getbuffer())
            ruta_temp = tmp.name
        
        logger.info(f"Archivo temporal creado: {ruta_temp}")
        
        # Validar tamaño
        validar_tamano_archivo(ruta_temp, max_mb=50)
        logger.info("Validación de tamaño exitosa")
        
        # Leer archivo con motor apropiado
        df_temp = leer_archivo_universal(ruta_temp, formato)
        
        # Validar que no esté vacío
        if df_temp.empty:
            raise ErrorDatos("El archivo está vacío o no contiene datos válidos.")
        
        # Detectar mapeo
        mapeo_detectado = detectar_mapeo_propuesto(df_temp)
        
        if mapeo_detectado:
            st.info("🔍 Se detectaron columnas en español:")
            st.text(mostrar_mapeo_propuesto(mapeo_detectado))
            aplicar_mapeo = st.checkbox("✅ Aplicar mapeo de columnas", value=True)
            
            if aplicar_mapeo:
                df = cargar_datos(ruta=ruta_temp, aplicar_mapeo=True)
                st.success("✅ Mapeo aplicado correctamente")
                logger.info(f"Mapeo aplicado: {len(mapeo_detectado)} columnas renombradas")
            else:
                df = cargar_datos(ruta=ruta_temp, aplicar_mapeo=False)
                logger.info("Mapeo no aplicado por decisión del usuario")
        else:
            st.info("📋 El archivo usa columnas en inglés (esquema estándar)")
            df = cargar_datos(ruta=ruta_temp, aplicar_mapeo=False)
            logger.info("Archivo en inglés detectado, sin mapeo necesario")
        
        return df
        
    except ErrorDatos as e:
        st.error(f"❌ Error en el archivo: {e}")
        logger.error(f"ErrorDatos en componente_carga_archivo: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Error inesperado: {e}")
        logger.error(f"Error inesperado en componente_carga_archivo: {e}", exc_info=True)
        return None
    finally:
        # Limpieza garantizada de archivo temporal
        if ruta_temp and os.path.exists(ruta_temp):
            try:
                os.unlink(ruta_temp)
                logger.info(f"Archivo temporal eliminado: {ruta_temp}")
            except Exception as e:
                logger.warning(f"No se pudo eliminar archivo temporal {ruta_temp}: {e}")


def componente_metricas_principales(df: pd.DataFrame) -> None:
    """Muestra las métricas principales de rotación.
    
    Args:
        df: DataFrame con los datos
    """
    try:
        col1, col2, col3 = st.columns(3)
        total_empleados = len(df)
        total_renuncias = len(df[df["Attrition"] == "Yes"])
        tasa_rotacion = (total_renuncias / total_empleados) * 100 if total_empleados > 0 else 0
        
        col1.metric("Total de empleados", total_empleados)
        col2.metric("Renuncias registradas", total_renuncias)
        col3.metric("Tasa de rotación", f"{tasa_rotacion:.1f}%")
        
        logger.debug(f"Métricas calculadas: {total_empleados} empleados, {tasa_rotacion:.1f}% rotación")
    except Exception as e:
        st.error("❌ Error calculando métricas principales")
        logger.error(f"Error en componente_metricas_principales: {e}", exc_info=True)


def componente_filtro_departamento(df: pd.DataFrame) -> pd.DataFrame:
    """Componente de filtro por departamento.
    
    Args:
        df: DataFrame original
        
    Returns:
        DataFrame filtrado
    """
    try:
        departamentos = ["Todos"] + sorted(df["Department"].unique().tolist())
        depto_elegido = st.selectbox("Filtrar por departamento:", departamentos)
        
        if depto_elegido != "Todos":
            df_filtrado = df[df["Department"] == depto_elegido]
            logger.info(f"Filtro aplicado: departamento {depto_elegido}, {len(df_filtrado)} registros")
        else:
            df_filtrado = df
            logger.info("Sin filtro de departamento")
            
        return df_filtrado
    except Exception as e:
        st.error("❌ Error en filtro de departamento")
        logger.error(f"Error en componente_filtro_departamento: {e}", exc_info=True)
        return df  # Retornar df original en caso de error


def componente_graficas_rotacion(df: pd.DataFrame) -> None:
    """Muestra gráficas de rotación por horas extra y satisfacción.
    
    Args:
        df: DataFrame con los datos
    """
    try:
        import plotly.express as px
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.histogram(
                df, x="OverTime", color="Attrition", barmode="group",
                title="Rotación según horas extra"
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.histogram(
                df, x="JobSatisfaction", color="Attrition", barmode="group",
                title="Rotación según satisfacción laboral"
            )
            st.plotly_chart(fig2, use_container_width=True)
            
        logger.debug("Gráficas de rotación renderizadas exitosamente")
    except Exception as e:
        st.error("❌ Error generando gráficas de rotación")
        logger.error(f"Error en componente_graficas_rotacion: {e}", exc_info=True)


def componente_indice_jdr(df: pd.DataFrame) -> None:
    """Muestra análisis del índice compuesto JD-R.
    
    Args:
        df: DataFrame con los datos
    """
    try:
        import plotly.express as px
        
        st.subheader("Índice compuesto JD-R (exploratorio)")
        
        if "indice_compuesto_jdr" not in df.columns:
            st.warning("⚠️ El índice JD-R no está calculado en los datos")
            logger.warning("Índice JD-R no encontrado en DataFrame")
            return
        
        indice_promedio = df["indice_compuesto_jdr"].mean()
        st.metric("Promedio del índice JD-R (plantilla filtrada)", f"{indice_promedio:.2f}")
        
        fig_jdr = px.histogram(
            df,
            x="indice_compuesto_jdr",
            color="Attrition",
            barmode="overlay",
            nbins=15,
            title="Distribución del índice compuesto JD-R, según rotación",
            labels={"indice_compuesto_jdr": "Índice compuesto JD-R (0 = menor desgaste, 14 = mayor desgaste)"},
            opacity=0.75,
        )
        fig_jdr.update_layout(bargap=0.1)
        st.plotly_chart(fig_jdr, use_container_width=True)
        
        st.warning(
            "⚠️ *Aviso ético:* Este índice compuesto es una métrica exploratoria "
            "inspirada conceptualmente en el modelo Job Demands-Resources (JD-R). "
            "No constituye un test psicométrico validado, un diagnóstico clínico, "
            "ni una evaluación de síndrome de burnout."
        )
        
        logger.debug(f"Componente índice JD-R renderizado, promedio: {indice_promedio:.2f}")
    except Exception as e:
        st.error("❌ Error en análisis del índice JD-R")
        logger.error(f"Error en componente_indice_jdr: {e}", exc_info=True)


def componente_explicabilidad_shap(project_root) -> None:
    """Muestra gráfico de explicabilidad SHAP.
    
    Args:
        project_root: Ruta raíz del proyecto
    """
    try:
        from pathlib import Path
        
        st.subheader("Explicabilidad del modelo (SHAP)")
        shap_path = project_root / "output" / "shap_resumen.png"
        
        if shap_path.exists():
            st.image(str(shap_path), caption="Variables que más influyen en la rotación, según SHAP")
            logger.debug("Gráfico SHAP renderizado exitosamente")
        else:
            st.info("📋 Archivo SHAP no encontrado. Ejecuta el modelo para generar explicabilidad.")
            logger.warning("Archivo SHAP no encontrado")
    except Exception as e:
        st.error("❌ Error cargando explicabilidad SHAP")
        logger.error(f"Error en componente_explicabilidad_shap: {e}", exc_info=True)


@st.cache_data
def _cargar_datos_preparados():
    """Carga y prepara datos con train_test_split. Cacheado para no recalcular."""
    from sklearn.model_selection import train_test_split
    from src.datos import cargar_datos
    df = cargar_datos()
    df_modelo = df.copy()
    for columna in df_modelo.select_dtypes(include="object").columns:
        df_modelo[columna] = df_modelo[columna].astype("category").cat.codes
    X = df_modelo.drop("Attrition", axis=1)
    y = df_modelo["Attrition"]
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return df, X_test, y_test


@st.cache_resource
def _cargar_modelo_cacheado(modelo_path_str):
    """Carga el modelo serializado con joblib. Cacheado como recurso."""
    from src.modelo import cargar_modelo
    return cargar_modelo(modelo_path_str)


@st.cache_data
def _calcular_metricas_cacheadas(_modelo, X_test, y_test):
    """Calcula métricas del modelo. Cacheado para no recalcular."""
    from src.modelo import evaluar_modelo
    return evaluar_modelo(_modelo, X_test, y_test)


@st.cache_data
def _calcular_shap_cacheado(_modelo, X_test):
    """Calcula SHAP values. Cacheado para no recalcular."""
    import shap
    explicador = shap.TreeExplainer(_modelo)
    return explicador(X_test)


def componente_modelo_prediccion(project_root):
    """Sección de modelo predictivo: métricas, predicción por empleado y explicación SHAP dinámica.

    Usa caching de Streamlit para evitar recálculos en cada renderizado:
    - Datos y train_test_split se cachean con @st.cache_data
    - Modelo se cachea con @st.cache_resource
    - Métricas y SHAP values se cachean con @st.cache_data
    """
    import shap
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    try:
        modelo_path = project_root / "output" / "modelo_vigia.joblib"
        if not modelo_path.exists():
            st.warning("Modelo no encontrado. Ejecuta src/modelo.py para generar el modelo predictivo.")
            logger.warning("Archivo modelo_vigia.joblib no encontrado")
            return

        # Cargar modelo serializado (cacheado)
        modelo = _cargar_modelo_cacheado(str(modelo_path))
        logger.info("Modelo cargado desde joblib")

        # Cargar datos preparados (cacheado)
        df, X_test, y_test = _cargar_datos_preparados()

        # Métricas (cacheadas)
        métricas = _calcular_metricas_cacheadas(modelo, X_test, y_test)
        st.subheader("Performance del Modelo Predictivo")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Accuracy", f"{métricas['accuracy']:.2%}")
        col2.metric("Precision", f"{métricas['precision']:.2%}")
        col3.metric("Recall", f"{métricas['recall']:.2%}")
        col4.metric("F1 Score", f"{métricas['f1']:.2%}")
        logger.info(
            f"Métricas del modelo: accuracy={métricas['accuracy']:.4f}, "
            f"precision={métricas['precision']:.4f}, recall={métricas['recall']:.4f}, "
            f"f1={métricas['f1']:.4f}"
        )

        # Selección de empleado
        st.subheader("Predicción por Empleado")
        opciones = [
            f"Empleado #{i} (Dept: {df.iloc[i]['Department']}, Age: {df.iloc[i]['Age']})"
            for i in range(len(df))
        ]
        idx_empleado = st.selectbox("Seleccionar empleado:", range(len(df)))

        empleado_features = X_test.iloc[[idx_empleado]]
        predicción = modelo.predict(empleado_features)[0]
        probabilidad = modelo.predict_proba(empleado_features)[0]

        col1, col2 = st.columns(2)
        etiqueta = "Rotación (Sí)" if predicción == 1 else "Se Queda (No)"
        col1.metric("Predicción del Modelo", etiqueta)
        col2.metric("Confianza", f"{max(probabilidad) * 100:.1f}%")
        col1.write(f"Prob. rotación: {probabilidad[1]:.2%}")
        col2.write(f"Prob. permanencia: {probabilidad[0]:.2%}")

        # Explicación SHAP dinámica (cacheada)
        st.subheader("Explicación de la Predicción (SHAP)")
        shap_values = _calcular_shap_cacheado(modelo, X_test)

        shap_empleado = pd.Series(
            shap_values.values[idx_empleado][:, 1],
            index=X_test.columns
        ).sort_values(key=abs, ascending=False)

        st.write("**Top 5 variables que influyen en esta predicción:**")
        for feature, valor in shap_empleado.head(5).items():
            direccion = "Mayor riesgo de rotación" if valor > 0 else "Menor riesgo de rotación"
            signo = "+" if valor > 0 else ""
            st.write(f"- **{feature}**: {signo}{valor:.4f} ({direccion})")

        # Gráfico de barras con matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        top_features = shap_empleado.head(10)
        colores = ["red" if v > 0 else "green" for v in top_features.values]
        ax.barh(range(len(top_features)), top_features.values, color=colores)
        ax.set_yticks(range(len(top_features)))
        ax.set_yticklabels(top_features.index)
        ax.set_xlabel("Impacto SHAP")
        ax.set_title("Top 10 variables que influyen en la predicción")
        ax.axvline(x=0, color="black", linestyle="--", linewidth=0.5)
        plt.tight_layout()
        st.pyplot(fig)

        logger.info(f"Explicación SHAP generada para empleado #{idx_empleado}")

    except Exception as e:
        st.error(f"Error en sección de modelo predictivo: {e}")
        logger.error(f"Error en componente_modelo_prediccion: {e}", exc_info=True)
