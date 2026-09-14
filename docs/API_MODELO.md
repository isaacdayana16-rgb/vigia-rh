# API del Modelo Predictivo

> **⚠️ Aviso ético:** El índice JD-R NO es un instrumento psicométrico validado, NO es diagnóstico clínico, y NO debe usarse para decisiones individuales de contratación, despido, ascenso o sanción. El dataset de demostración es IBM HR Analytics Employee Attrition (dataset público de Kaggle), no datos reales de empleados.

---

## Visión general

`src.modelo` expone 5 funciones modulares para el ciclo completo de un modelo predictivo de rotación de personal basado en RandomForestClassifier (scikit-learn). El modelo se entrena, evalúa, serializa con joblib, y se carga desde el dashboard Streamlit o de forma standalone.

## Instalación

```bash
pip install -e .
```

## Importación

```python
from src.modelo import (
    entrenar_modelo,
    evaluar_modelo,
    guardar_modelo,
    cargar_modelo,
    obtener_importancias,
)
```

---

## `entrenar_modelo(df)`

Entrena un `RandomForestClassifier` para predecir rotación de empleados.

**Parámetros:**
- `df` (`pd.DataFrame`): DataFrame con datos de empleados, esquema IBM HR (8 columnas requeridas: `Attrition`, `OverTime`, `JobSatisfaction`, `MonthlyIncome`, `Department`, `DistanceFromHome`, `WorkLifeBalance`, `RelationshipSatisfaction`).

**Retorna:** `tuple(modelo, X_test, y_test)`
- `modelo`: `RandomForestClassifier` entrenado (200 estimadores, `random_state=42`).
- `X_test`: Features de prueba (`pd.DataFrame`).
- `y_test`: Labels de prueba (`pd.Series`).

**Comportamiento:**
- Codifica automáticamente columnas categóricas (`object`) a códigos numéricos mediante `cat.codes`.
- Divide el dataset en train/test con `test_size=0.2` y `random_state=42`.
- No modifica el DataFrame original (trabaja con copia).

**Ejemplo:**
```python
from src.datos import cargar_datos
from src.modelo import entrenar_modelo

df = cargar_datos()
modelo, X_test, y_test = entrenar_modelo(df)
```

---

## `evaluar_modelo(modelo, X_test, y_test)`

Evalúa el rendimiento del modelo entrenado.

**Parámetros:**
- `modelo`: `RandomForestClassifier` entrenado.
- `X_test` (`pd.DataFrame`): Features de prueba.
- `y_test` (`pd.Series`): Labels reales de prueba.

**Retorna:** `dict` con las siguientes claves:
| Clave | Tipo | Descripción |
|---|---|---|
| `accuracy` | `float` | Proporción de predicciones correctas (0.0–1.0) |
| `precision` | `float` | Precision para la clase positiva (rotación = "Yes") |
| `recall` | `float` | Recall para la clase positiva |
| `f1` | `float` | F1-score para la clase positiva |

**Ejemplo:**
```python
from src.modelo import evaluar_modelo

métricas = evaluar_modelo(modelo, X_test, y_test)
print(f"Accuracy: {métricas['accuracy']:.2%}")
```

**Nota:** `pos_label=1` se usa para todas las métricas de clasificación. La etiqueta positiva corresponde a `Attrition == "Yes"`.

---

## `guardar_modelo(modelo, ruta)`

Serializa el modelo entrenado con joblib.

**Parámetros:**
- `modelo`: Modelo entrenado.
- `ruta` (`str` o `Path`): Ruta del archivo `.joblib` de destino.

**Retorna:** `None`

**Ejemplo:**
```python
from src.modelo import guardar_modelo

guardar_modelo(modelo, "output/modelo_vigia.joblib")
```

---

## `cargar_modelo(ruta)`

Deserializa un modelo previamente guardado con joblib.

**Parámetros:**
- `ruta` (`str` o `Path`): Ruta al archivo `.joblib`.

**Retorna:** `RandomForestClassifier` cargado.

**Ejemplo:**
```python
from src.modelo import cargar_modelo

modelo = cargar_modelo("output/modelo_vigia.joblib")
```

---

## `obtener_importancias(modelo, X)`

Retorna las importancias de features ordenadas de mayor a menor.

**Parámetros:**
- `modelo`: `RandomForestClassifier` entrenado.
- `X` (`pd.DataFrame`): DataFrame de features (debe tener los nombres de columna originales).

**Retorna:** `pd.Series` con los nombres de columna como índice y las importancias como valores, ordenados descendentemente.

**Ejemplo:**
```python
from src.modelo import obtener_importancias

importancias = obtener_importancias(modelo, X_test)
print(importancias.head(10))
```

---

## Uso completo del pipeline

```python
from src.datos import cargar_datos
from src.modelo import entrenar_modelo, evaluar_modelo, guardar_modelo, cargar_modelo, obtener_importancias

# 1. Cargar datos
df = cargar_datos()

# 2. Entrenar modelo
modelo, X_test, y_test = entrenar_modelo(df)

# 3. Evaluar
métricas = evaluar_modelo(modelo, X_test, y_test)
print(f"Accuracy: {métricas['accuracy']:.2%}")

# 4. Guardar
guardar_modelo(modelo, "output/modelo_vigia.joblib")

# 5. Cargar en otro contexto
modelo_cargado = cargar_modelo("output/modelo_vigia.joblib")

# 6. Inspeccionar importancias
importancias = obtener_importancias(modelo_cargado, X_test)
print(importancias.head(5))
```

---

## Integración con explicabilidad SHAP

`src.explicabilidad` depende de `src.modelo`:

```python
from src.modelo import cargar_modelo
from src.explicabilidad import generar_explicacion_empleado, obtener_top_variables

modelo = cargar_modelo("output/modelo_vigia.joblib")
expl = generar_explicacion_empleado(modelo, X_test, empleado_index=0)
top = obtener_top_variables(expl, top_n=5)
```

---

## Compromiso ético

Este modelo es exploratorio. El dataset es público (Kaggle). El índice JD-R no constituye diagnóstico clínico ni instrumento psicométrico validado. No debe usarse para decisiones individuales de personal.
