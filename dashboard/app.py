import streamlit as st
import plotly.express as px
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datos import cargar_datos, validar_columnas, agregar_indice_compuesto_jdr
st.set_page_config(page_title="Vigía RH", layout="wide")

st.title("🔎 Vigía RH — Analítica Predictiva de Rotación")
st.markdown("Sistema de análisis de riesgo de rotación de personal")

# Cargar datos (ruta centralizada + validación de esquema)
df = cargar_datos()
df = agregar_indice_compuesto_jdr(df)

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
st.subheader("Índice compuesto JD-R (exploratorio)")

indice_promedio = df_filtrado["indice_compuesto_jdr"].mean()
st.metric("Promedio del índice JD-R (plantilla filtrada)", f"{indice_promedio:.2f}")

fig_jdr = px.histogram(
    df_filtrado,
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

st.warning("⚠️ *Aviso ético:* Este índice compuesto es una métrica exploratoria inspirada conceptualmente en el modelo Job Demands-Resources (JD-R). No constituye un test psicométrico validado, un diagnóstico clínico, ni una evaluación de síndrome de burnout.")

st.divider()
st.subheader("Explicabilidad del modelo (SHAP)")
shap_path = PROJECT_ROOT / "output" / "shap_resumen.png"
st.image(str(shap_path), caption="Variables que más influyen en la rotación, según SHAP")