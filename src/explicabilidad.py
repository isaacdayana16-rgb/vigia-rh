import pandas as pd
import shap
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Cargar y preparar los datos (igual que en modelo.py)
df = pd.read_csv("../data/WA_Fn-UseC_-HR-Employee-Attrition.csv")
df_modelo = df.copy()
for columna in df_modelo.select_dtypes(include="object").columns:
    df_modelo[columna] = df_modelo[columna].astype("category").cat.codes

X = df_modelo.drop("Attrition", axis=1)
y = df_modelo["Attrition"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Entrenar el modelo otra vez
modelo = RandomForestClassifier(n_estimators=200, random_state=42)
modelo.fit(X_train, y_train)

# Crear el explicador SHAP
explicador = shap.TreeExplainer(modelo)
valores_shap = explicador(X_test)

# Explicar UN empleado específico (el primero del grupo de prueba)
empleado_index = 0
print(f"\n--- Explicación para el empleado #{empleado_index} ---")
print(f"Riesgo real de este empleado (0=se queda, 1=renuncia): {y_test.iloc[empleado_index]}")

# Ver qué variables más empujaron la predicción de ESTE empleado
shap_del_empleado = pd.Series(
    valores_shap.values[empleado_index][:, 1],
    index=X_test.columns
).sort_values(key=abs, ascending=False)

print("\nLas 5 variables que más influyeron en la predicción de este empleado:")
print(shap_del_empleado.head(5))

# Guardar un resumen visual (gráfica) de qué variables más pesan en general
import matplotlib
matplotlib.use("Agg")  # para que no intente abrir ventana
import matplotlib.pyplot as plt

shap.summary_plot(valores_shap[:, :, 1], X_test, show=False)
plt.tight_layout()
plt.savefig("../output/shap_resumen.png")
print("\nGráfica de SHAP guardada en output/shap_resumen.png")
