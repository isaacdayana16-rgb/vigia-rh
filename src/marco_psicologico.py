import pandas as pd

df = pd.read_csv("../data/WA_Fn-UseC_-HR-Employee-Attrition.csv")

# Mapeamos variables del dataset a dimensiones del modelo
# Job Demands-Resources (JD-R): las "demandas" desgastan, los "recursos" protegen

# DEMANDAS (lo que agota al empleado)
df["demanda_horas_extra"] = df["OverTime"].map({"Yes": 1, "No": 0})
df["demanda_distancia"] = df["DistanceFromHome"]

# RECURSOS (lo que protege al empleado del desgaste)
df["recurso_satisfaccion"] = df["JobSatisfaction"]
df["recurso_balance_vida"] = df["WorkLifeBalance"]
df["recurso_relacion_jefe"] = df["RelationshipSatisfaction"]

# Índice simple de "riesgo de burnout" (demandas altas + recursos bajos)
df["indice_burnout"] = (
    df["demanda_horas_extra"] * 2
    + (5 - df["recurso_satisfaccion"])
    + (5 - df["recurso_balance_vida"])
    + (5 - df["recurso_relacion_jefe"])
)

# ¿El índice de burnout se relaciona con la rotación real?
print("Índice de burnout promedio, según si la persona renunció o no:")
print(df.groupby("Attrition")["indice_burnout"].mean())

print("\nEsto confirma (o no) si nuestra lectura psicológica del JD-R")
print("coincide con lo que el modelo predictivo encontró por su cuenta.")