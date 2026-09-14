import sys
from pathlib import Path

PROJECT_ROOT = Path.cwd()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from src.datos import cargar_datos, agregar_indice_compuesto_jdr
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import joblib


def entrenar_modelo(df):
    """Entrena un RandomForestClassifier para predecir rotación de empleados.

    Args:
        df: DataFrame con datos de empleados (schema IBM HR).

    Returns:
        tuple: (modelo, X_test, y_test) donde modelo es el RandomForestClassifier
        entrenado, X_test y y_test son los datos de prueba.
    """
    df_modelo = df.copy()
    for columna in df_modelo.select_dtypes(include="object").columns:
        df_modelo[columna] = df_modelo[columna].astype("category").cat.codes

    X = df_modelo.drop("Attrition", axis=1)
    y = df_modelo["Attrition"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    modelo = RandomForestClassifier(n_estimators=200, random_state=42)
    modelo.fit(X_train, y_train)

    return modelo, X_test, y_test


def evaluar_modelo(modelo, X_test, y_test):
    """Evalúa el modelo y retorna métricas de performance.

    Args:
        modelo: RandomForestClassifier entrenado.
        X_test: Features de prueba.
        y_test: Labels reales de prueba.

    Returns:
        dict con accuracy, precision, recall, f1.
    """
    predicciones = modelo.predict(X_test)
    return {
        "accuracy": accuracy_score(y_test, predicciones),
        "precision": precision_score(y_test, predicciones, pos_label=1),
        "recall": recall_score(y_test, predicciones, pos_label=1),
        "f1": f1_score(y_test, predicciones, pos_label=1),
    }


def guardar_modelo(modelo, ruta):
    """Serializa el modelo con joblib.

    Args:
        modelo: Modelo entrenado.
        ruta: Ruta donde guardar el archivo .joblib.
    """
    joblib.dump(modelo, ruta)


def cargar_modelo(ruta):
    """Deserializa un modelo guardado con joblib.

    Args:
        ruta: Ruta al archivo .joblib.

    Returns:
        Modelo cargado.
    """
    return joblib.load(ruta)


def obtener_importancias(modelo, X):
    """Retorna las importancias de features ordenadas de mayor a menor.

    Args:
        modelo: RandomForestClassifier entrenado.
        X: DataFrame de features.

    Returns:
        pd.Series con las importancias ordenadas.
    """
    importancias = pd.Series(modelo.feature_importances_, index=X.columns)
    importancias = importancias.sort_values(ascending=False)
    return importancias


if __name__ == "__main__":
    df = cargar_datos()
    modelo, X_test, y_test = entrenar_modelo(df)
    métricas = evaluar_modelo(modelo, X_test, y_test)

    print(f"Precisión del modelo: {métricas['accuracy']:.2%}")
    print(f"Precision: {métricas['precision']:.2%}")
    print(f"Recall: {métricas['recall']:.2%}")
    print(f"F1: {métricas['f1']:.2%}")
    print("\nReporte completo:")
    print(classification_report(y_test, modelo.predict(X_test)))

    importancias = obtener_importancias(modelo, X_test)
    print("\nLas 10 variables que más influyen en el riesgo de rotación:")
    print(importancias.head(10))
