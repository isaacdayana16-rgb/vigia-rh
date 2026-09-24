"""Validación: validez de constructo (análisis factorial) y de criterio.

Implementado con numpy puro:
- analisis_factorial: extrae factores vía eigendecomposition de la matriz de
  correlaciones (aproximación de ejes principales).
- regresion_logistica: descenso de gradiente con regularización L2.
"""
import numpy as np
import pandas as pd


def _rotacion_varimax(cargas, gamma: float = 1.0, n_iter: int = 500, tol: float = 1e-6):
    """Rotación ortogonal varimax (Kaiser) para cargas factoriales.

    Maximiza la varianza de las cargas al cuadrado para obtener una
    estructura factorial más interpretable (cada ítem carga en pocos factores).

    Returns:
        (cargas_rotadas, matriz_rotacion)
    """
    X = np.asarray(cargas, dtype=float).copy()
    p, k = X.shape
    R = np.eye(k)
    d = 0.0
    for _ in range(n_iter):
        old_d = d
        # Normalizar filas
        normas = np.linalg.norm(X, axis=1, keepdims=True)
        normas[normas < 1e-12] = 1.0
        U = X / normas
        # Matriz B de Kaiser
        B = U.T @ (U**3 - (1.0 / p) * np.outer(np.ones(p), np.sum(U**2, axis=0)))
        # SVD para hallar la rotación óptima
        Vt, _, Wt = np.linalg.svd(B)
        phi = Wt @ Vt
        X = X @ phi
        R = R @ phi
        d = float(np.sum(B * phi))
        if old_d != 0.0 and abs(d - old_d) < tol:
            break
    return X, R


def analisis_factorial(df_items: pd.DataFrame, n_factores: int = 2, rotacion: bool = True):
    """Análisis factorial exploratorio (extracción de ejes principales).

    Args:
        df_items: DataFrame con columnas = ítems.
        n_factores: Número de factores a extraer.
        rotacion: Si True, aplica rotación varimax.

    Returns:
        (cargas, varianza):
            cargas: DataFrame con las cargas factoriales (ítems x factores).
            varianza: ndarray con la varianza explicada por factor.
    """
    n_filas, n_cols = df_items.shape
    # Protección: se necesitan al menos 2 observaciones y 2 ítems para correlacionar
    if n_filas < 2 or n_cols < 2:
        nombres = [f"F{i + 1}" for i in range(n_factores)]
        cargas_vacio = pd.DataFrame(0.0, index=df_items.columns, columns=nombres)
        return cargas_vacio, np.zeros(n_factores)

    corr = np.corrcoef(df_items.to_numpy(dtype=float).T)
    # Protección: valores NaN en la correlación (varianza nula en algún ítem)
    if not np.isfinite(corr).all():
        nombres = [f"F{i + 1}" for i in range(n_factores)]
        cargas_vacio = pd.DataFrame(0.0, index=df_items.columns, columns=nombres)
        return cargas_vacio, np.zeros(n_factores)

    eigvals, eigvecs = np.linalg.eigh(corr)
    # Ordenar descendente
    orden = np.argsort(eigvals)[::-1][:n_factores]
    cargas = eigvecs[:, orden] * np.sqrt(eigvals[orden])
    varianza = eigvals[orden] / np.sum(eigvals)
    nombres = [f"F{i + 1}" for i in range(n_factores)]

    if rotacion:
        cargas_rotadas, _ = _rotacion_varimax(cargas)
        cargas = cargas_rotadas

    cargas_df = pd.DataFrame(cargas, index=df_items.columns, columns=nombres)
    return cargas_df, varianza


def regresion_logistica(
    X: pd.DataFrame,
    y: np.ndarray,
    tasa: float = 0.01,
    epocas: int = 2000,
    l2: float = 1e-3,
) -> dict:
    """Regresión logística binaria por descenso de gradiente (L2).

    Args:
        X: DataFrame de predictores (sin intercepto).
        y: ndarray binario (0/1).
        tasa: Tasa de aprendizaje.
        epocas: Iteraciones de descenso de gradiente.
        l2: Fuerza de regularización L2.

    Returns:
        dict con 'coeficientes' (serie) y 'intercepto'.
    """
    Xn = np.column_stack([np.ones(len(X)), X.to_numpy(dtype=float)])
    w = np.zeros(Xn.shape[1])
    y_arr = np.asarray(y, dtype=float)
    for _ in range(epocas):
        p = 1.0 / (1.0 + np.exp(-Xn @ w))
        grad = Xn.T @ (p - y_arr)
        # Regularizar solo pesos de predictores, no el intercepto
        grad[1:] += l2 * w[1:]
        w -= tasa * grad

    nombres = ["intercepto"] + list(X.columns)
    coeficientes = pd.Series(w, index=nombres)
    return {"coeficientes": coeficientes, "intercepto": float(w[0])}


def validacion_cruzada_estratificada(X, y, k: int = 5, semilla: int = 42) -> dict:
    """Validación cruzada k-fold ESTRATIFICADA con métricas balanceadas.

    Reporta F1 macro y balanced accuracy (NO accuracy simple): el
    instrumento suele concentrar las respuestas en "riesgo bajo", lo que
    hace que la accuracy simple sea engañosa frente a clases desbalanceadas.

    Args:
        X: DataFrame/ndarray de predictores.
        y: ndarray binario (0/1).
        k: Número de folds (>= 5 recomendado).
        semilla: Semilla para el shuffle estratificado.

    Returns:
        dict con 'viable' (False si alguna clase tiene menos de k miembros),
        'k', 'n', 'clases' (conteo por clase), 'f1_macro', 'balanced_accuracy'
        y 'etiqueta' ("exploratorio_no_generalizable" si n < 100;
        "indicativo" en caso contrario).
    """
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import balanced_accuracy_score, f1_score

    y_arr = np.asarray(y)
    clases = {int(c): int((y_arr == c).sum()) for c in np.unique(y_arr)}

    base = {"k": int(k), "n": int(len(y_arr)), "clases": clases}
    if any(c < k for c in clases.values()):
        return {
            **base,
            "viable": False,
            "f1_macro": None,
            "balanced_accuracy": None,
            "etiqueta": "no_viable_clase_insuficiente",
        }

    skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=semilla)
    modelo = LogisticRegression(max_iter=1000)
    pred = cross_val_predict(modelo, np.asarray(X, dtype=float), y_arr, cv=skf)

    etiqueta = "exploratorio_no_generalizable" if len(y_arr) < 100 else "indicativo"
    return {
        **base,
        "viable": True,
        "f1_macro": float(f1_score(y_arr, pred, average="macro")),
        "balanced_accuracy": float(balanced_accuracy_score(y_arr, pred)),
        "etiqueta": etiqueta,
    }