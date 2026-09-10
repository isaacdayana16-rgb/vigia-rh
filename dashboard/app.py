import streamlit as st
import plotly.express as px
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datos import cargar_datos, validar_columnas
st.set_page_config(page_title="Vigía RH", layout="wide")

st.title("🔎 Vigía RH — Analítica Predictiva de Rotación")
st.markdown("Sistema de análisis de riesgo de rotación de personal")

# Cargar datos (ruta centralizada + validación de esquema)
df = cargar_datos()

# Métricas generales arriba
col1, col2, col3 = st.columns(3)
total_empleados = len(df)
total_renuncias = len(df[df["Attrition"] == "Yes"])
tasa_rotacion = (total_renuncias / total_empleados) * 100

col1.metric("Total de empleados", total_empleados)
col2.metric("Renuncias registradas", total_renuncias)
col3.metric("Tasa de rotación", f"{tasa_rotacion:.1f}%")

st.divider()

# Filtro interactivo por departamento
departamentos = ["Todos"] + df["Department"].unique().tolist()
depto_elegido = st.selectbox("Filtrar por departamento:", departamentos)

if depto_elegido != "Todos":
    df_filtrado = df[df["Department"] == depto_elegido]
else:
    df_filtrado = df

# Gráficas interactivas
col1, col2 = st.columns(2)

with col1:
    fig1 = px.histogram(df_filtrado, x="OverTime", color="Attrition", barmode="group",
                         title="Rotación según horas extra")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.histogram(df_filtrado, x="JobSatisfaction", color="Attrition", barmode="group",
                         title="Rotación según satisfacción laboral")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.subheader("Explicabilidad del modelo (SHAP)")
st.image("output/shap_resumen.png", caption="Variables que más influyen en la rotación, según SHAP")