import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Cargar los datos
df = pd.read_csv("../data/WA_Fn-UseC_-HR-Employee-Attrition.csv")

# Convertir texto a números (el modelo solo entiende números)
df_modelo = df.copy()
for columna in df_modelo.select_dtypes(include="object").columns:
    df_modelo[columna] = df_modelo[columna].astype("category").cat.codes

# Separar la variable que queremos predecir (Attrition) del resto
X = df_modelo.drop("Attrition", axis=1)
y = df_modelo["Attrition"]

# Dividir en datos de entrenamiento y datos de prueba
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Crear y entrenar el modelo
modelo = RandomForestClassifier(n_estimators=200, random_state=42)
modelo.fit(X_train, y_train)

# Probar qué tan bien predice
predicciones = modelo.predict(X_test)
precision = accuracy_score(y_test, predicciones)

print(f"Precisión del modelo: {precision:.2%}")
print("\nReporte completo:")
print(classification_report(y_test, predicciones))

# Ver qué variables pesan más en la predicción
importancias = pd.Series(modelo.feature_importances_, index=X.columns)
importancias = importancias.sort_values(ascending=False)
print("\nLas 10 variables que más influyen en el riesgo de rotación:")
print(importancias.head(10))