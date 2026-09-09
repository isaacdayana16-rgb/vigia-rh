import pandas as pd
import plotly.express as px

df = pd.read_csv("../data/WA_Fn-UseC_-HR-Employee-Attrition.csv")

print("Datos vacíos por columna:")
print(df.isnull().sum().sum())

fig1 = px.histogram(df, x="OverTime", color="Attrition", barmode="group",
                     title="Rotación según si hace horas extra")
fig1.write_html("../output/grafica1_horas_extra.html")

fig2 = px.histogram(df, x="Department", color="Attrition", barmode="group",
                     title="Rotación por departamento")
fig2.write_html("../output/grafica2_departamento.html")

fig3 = px.histogram(df, x="JobSatisfaction", color="Attrition", barmode="group",
                     title="Rotación según satisfacción laboral")
fig3.write_html("../output/grafica3_satisfaccion.html")

print("Listo, las 3 gráficas se guardaron en la carpeta output")

