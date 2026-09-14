import sys
from pathlib import Path

PROJECT_ROOT = Path.cwd()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import shap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from src.datos import cargar_datos
from src.modelo import cargar_modelo


def preparar_datos():
    """Carga datos, codifica categorías y divide en train/test.

    Returns:
        tuple: (df, X_test, y_test) con datos codificados y divididos.
    """
    df = cargar_datos()
    df_modelo = df.copy()
    for columna in df_modelo.select_dtypes(include="object").columns:
        df_modelo[columna] = df_modelo[columna].astype("category").cat.codes

    X = df_modelo.drop("Attrition", axis=1)
    y = df_modelo["Attrition"]

    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    return df, X_test, y_test


def generar_explicacion_empleado(modelo, X_test, empleado_index=0):
    """Explica la predicción de un empleado específico usando SHAP.

    Args:
        modelo: RandomForestClassifier entrenado.
        X_test: Features de prueba.
        empleado_index: Índice del empleado a explicar.

    Returns:
        pd.Series con los valores SHAP ordenados por impacto absoluto.
    """
    explicador = shap.TreeExplainer(modelo)
    shap_values = explicador(X_test)

    shap_empleado = pd.Series(
        shap_values.values[empleado_index][:, 1],
        index=X_test.columns
    ).sort_values(key=abs, ascending=False)

    return shap_empleado


def generar_grafica_shap(modelo, X_test, ruta_destino):
    """Genera y guarda la gráfica de resumen SHAP para todos los empleados.

    Args:
        modelo: RandomForestClassifier entrenado.
        X_test: Features de prueba.
        ruta_destino: Ruta donde guardar el PNG.
    """
    explicador = shap.TreeExplainer(modelo)
    shap_values = explicador(X_test)

    shap.summary_plot(shap_values[:, :, 1], X_test, show=False)
    plt.tight_layout()
    plt.savefig(ruta_destino)
    plt.close()


def obtener_top_variables(shap_series, top_n=5):
    """Retorna las top N variables más influyentes de una explicación SHAP.

    Args:
        shap_series: pd.Series con valores SHAP de un empleado.
        top_n: Número de variables a retornar.

    Returns:
        pd.Series con las top_n variables ordenadas por impacto.
    """
    return shap_series.head(top_n)


if __name__ == "__main__":
    df, X_test, y_test = preparar_datos()

    modelo_path = PROJECT_ROOT / "output" / "modelo_vigia.joblib"
    modelo = cargar_modelo(str(modelo_path))

    shap_values = generar_explicacion_empleado(modelo, X_test)
    top = obtener_top_variables(shap_values)

    print(f"\n--- Top variables que influyen en la rotacion ---")
    for feature, valor in top.items():
        direccion = "Mayor riesgo" if valor > 0 else "Menor riesgo"
        print(f"  {feature}: {valor:+.4f} ({direccion})")

    generar_grafica_shap(modelo, X_test, str(PROJECT_ROOT / "output" / "shap_resumen.png"))
    print(f"\nGrafica SHAP guardada en output/shap_resumen.png")
