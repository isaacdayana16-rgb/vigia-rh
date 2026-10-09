# 📋 AUDITORÍA TÉCNICA SENIOR — REPOSITORIO "VIGÍA RH"

**Fecha de auditoría:** Octubre 2026  
**Auditor:** Revisor Técnico Senior / Arquitecto de Software & People Analytics  
**Estado general del repositorio:** Proyecto en transición arquitectónica activa. Conviven dos paradigmas inconexos (analítica predictiva de rotación con IBM HR vs. psicometría y factores psicosociales con el instrumento oficial del MDT de Ecuador). Test suite robusta en psicometría (201/201 tests aprobados), pero con deudas críticas de integración, higiene de código y coherencia de producto.

---

## 1. Mapa del Proyecto

### 1.1 Árbol de Directorios y Archivos

```
vigia-rh/
├── .devcontainer/
│   └── devcontainer.json               # Configuración de entorno en contenedor VS Code / Codespaces
├── .github/
│   └── workflows/
│       └── test.yml                    # Pipeline CI en GitHub Actions (matriz Python 3.11, 3.12, 3.13)
├── .streamlit/
│   └── config.toml                     # Configuración de servidor Streamlit (puerto 8501, headless)
├── dashboard/
│   └── app.py                          # Entry point principal de la aplicación Streamlit
├── data/
│   ├── encuestas/
│   │   └── plantilla_respuestas.csv    # Cabeceras CSV con esquema oficial MDT (58 ítems + demográficos)
│   ├── RH_Empresa_Ejemplo_Ecuador.xlsx # Dataset de juguete (10 filas) con columnas traducidas de IBM HR
│   └── WA_Fn-UseC_-HR-Employee-Attrition.csv # Dataset público IBM HR Analytics (1470 filas, Kaggle)
├── docs/
│   ├── fuentes/
│   │   ├── guia_aplicacion_cuestionario_mdt_ecuador.pdf # Fuente primaria oficial del MDT (Octubre 2018)
│   │   └── guia_mdt_extracto_texto.txt # Transcripción textual de secciones normativas y baremos
│   ├── API_MODELO.md                   # Documentación técnica de las funciones en src/modelo.py
│   ├── CONSENTIMIENTO.md               # Modelo de consentimiento informado acorde a LOPDP Ecuador
│   ├── CUESTIONARIO.md                # Texto literal de los 58 ítems del cuestionario oficial MDT
│   ├── GUIA_RECOLECCION.md             # Manual operativo para recolección en campo (Google Forms)
│   └── PROTOCOLO_SITUACIONES_DETECTADAS.md # Protocolo de derivación ante acoso o riesgo psicosocial
├── logs/                               # Directorio de logs de ejecución (generados por VigiaLogger)
├── notebooks/
│   ├── explorar.py                     # Script exploratorio básico (IBM HR)
│   └── graficas.py                     # Script de generación de histogramas HTML Plotly (IBM HR)
├── output/
│   ├── grafica1_horas_extra.html       # Gráfico HTML pregenerado (4.3 MB, huérfano)
│   ├── grafica2_departamento.html      # Gráfico HTML pregenerado (4.3 MB, huérfano)
│   ├── grafica3_satisfaccion.html      # Gráfico HTML pregenerado (4.3 MB, huérfano)
│   ├── modelo_vigia.joblib             # Modelo RandomForest serializado (IBM HR)
│   ├── reporte_validacion_psicometria.pdf # Reporte PDF generado de la vía psicométrica
│   ├── reporte_vigia_rh.pdf            # Reporte PDF generado de la vía IBM HR / JD-R
│   └── shap_resumen.png                # Imagen estática de resumen de valores SHAP (IBM HR)
├── src/
│   ├── __init__.py                     # Declaración de paquete raíz
│   ├── datos.py                        # Carga, validación (IBM HR) y cálculo del índice JD-R proxy
│   ├── explicabilidad.py               # Módulo huérfano de SHAP sobre modelo IBM HR
│   ├── marco_psicologico.py            # Script conceptual de comparación JD-R vs Attrition
│   ├── modelo.py                       # Entrenamiento y serialización de RandomForest sobre IBM HR
│   ├── reportes.py                     # Generación de reporte PDF clásico (IBM HR / JD-R) con fpdf2
│   ├── simulador_intervencion.py       # Simulador de impacto organizacional informado por meta-análisis
│   ├── dashboard/
│   │   ├── __init__.py                 # Exportación de componentes UI
│   │   ├── error_handler.py            # Excepciones custom (VigiaError) y decoradores
│   │   └── ui_components.py            # Componentes Streamlit de carga, filtros, gráficos y predicción
│   ├── psicometria/
│   │   ├── __init__.py                 # Exportación pública del subsistema psicométrico
│   │   ├── __main__.py                 # Entry point: python -m src.psicometria
│   │   ├── calidad_datos.py            # Control de calidad (rango 1-4, duplicados, varianza cero)
│   │   ├── cli.py                      # CLI de validación psicométrica y generador de reportes
│   │   ├── ejemplos_datos.py           # Generador sintético de respuestas MDT (N configurable)
│   │   ├── fiabilidad.py               # Cronbach α, McDonald ω, Spearman-Brown (NumPy puro)
│   │   ├── instrumento.py              # Definición de 58 ítems, 8 dimensiones y puntos de corte MDT
│   │   ├── puntuaciones.py             # Sumatoria simple oficial y puntuaciones normalizadas
│   │   ├── reporte.py                  # Generación de reporte en texto plano y PDF psicométrico
│   │   ├── simulador_muestra.py        # Simulación de tamaño muestral N vs fiabilidad esperada
│   │   ├── validacion.py               # AFE (varimax), regresión logística y CV estratificada
│   │   └── vista_dashboard.py          # Componente Streamlit para visualización de perfiles MDT
│   └── utils/
│       ├── __init__.py
│       └── logger.py                   # Logger estructurado centralizado (VigiaLogger)
├── tests/
│   ├── __init__.py
│   ├── conftest.py                     # Configuración de path para ejecución de pytest
│   ├── test_calidad_datos.py           # Pruebas de limpieza y validación de encuestas
│   ├── test_dashboard.py               # Pruebas unitarias de componentes UI y manejo de errores
│   ├── test_datos.py                   # Pruebas de carga, esquemas IBM HR y cálculo JD-R
│   ├── test_psicometria.py             # Pruebas de baremos, fiabilidad, AFE y CV estratificada
│   ├── test_psicometria_cli.py         # Pruebas funcionales de interfaz de consola y reportes
│   ├── test_simulador_intervencion.py  # Pruebas del catálogo de intervención y proyecciones
│   └── test_vista_dashboard.py         # Pruebas de la sección psicométrica de Streamlit
├── .gitignore                          # Ignora venv, caches, logs y data/RH_Empresa_Ejemplo_Ecuador.xlsx
├── Dockerfile                          # Imagen Debian-slim con Python 3.11 y Streamlit
├── pyproject.toml                      # Metadatos del paquete (pip install -e .)
├── README.md                           # Documentación general y manual de usuario
├── requirements.txt                    # Dependencias congeladas del proyecto
└── start_dashboard_safe.py             # Script de arranque vigilado y limpieza de puerto para Streamlit
```

---

### 1.2 Propósito de los Módulos y Flujo de Interconexión

El repositorio contiene **dos subsistemas desacoplados** que conviven en el mismo código:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ SUBSISTEMA 1: Analítica Predictiva de Rotación (Legacy / IBM HR)                        │
│                                                                                        │
│  data/WA_Fn-UseC_-HR-Employee-Attrition.csv ──► src/datos.py (esquema IBM HR + JD-R)   │
│                                                   │                                    │
│        ┌──────────────────────────────────────────┼─────────────────────────┐          │
│        ▼                                          ▼                         ▼          │
│  src/modelo.py                             src/reportes.py       src/marco_psicologico │
│   (RandomForest)                                (PDF)                 (análisis CLI)   │
│        │                                                                               │
│        ▼                                                                               │
│  output/modelo_vigia.joblib                                                            │
│        │                                                                               │
│        ▼                                                                               │
│  src/dashboard/ui_components.py (componente_modelo_prediccion + explicabilidad_shap)    │
│        │                                                                               │
│        ▼                                                                               │
│  dashboard/app.py (primeras 80 líneas del dashboard)                                   │
└────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────┐
│ SUBSISTEMA 2: Psicometría y Riesgo Psicosocial (Instrumento Oficial MDT Ecuador)       │
│                                                                                        │
│  docs/fuentes/ ──► src/psicometria/instrumento.py (58 ítems, 8 dimensiones, baremos)   │
│                             │                                                          │
│        ┌────────────────────┴─────────────────────────────────────────┐                │
│        ▼                                                              ▼                │
│  data/encuestas/*.csv (o ejemplos_datos.py si no hay)     src/psicometria/puntuaciones │
│        ▼                                                              ▼                │
│  src/psicometria/calidad_datos.py                         fiabilidad / validacion      │
│        ▼                                                              │                │
│  src/psicometria/cli.py ──► output/reporte_validacion.pdf ◄───────────┘                │
│        │                                                                               │
│        ▼                                                                               │
│  src/psicometria/vista_dashboard.py ──► dashboard/app.py (líneas 84-86, aditivo)       │
│                                                                                        │
│  [HUÉRFANO EN UI] src/simulador_intervencion.py (solo CLI: python -m src.simulador...) │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **`src/datos.py`**: Puerta de entrada del subsistema 1. Carga `data/WA_Fn-UseC_-HR-Employee-Attrition.csv`, normaliza variables booleanas y calcula `indice_compuesto_jdr` combinando 4 columnas de IBM HR.
2. **`src/modelo.py`**: Entrena un `RandomForestClassifier` sobre los datos de IBM para predecir la columna binaria `Attrition`.
3. **`src/dashboard/`**: Implementa `ui_components.py` y `error_handler.py`. Carga datos, renderiza KPIs de rotación, histogramas JD-R, y realiza inferencia sobre el modelo serializado `output/modelo_vigia.joblib`.
4. **`src/psicometria/`**: Núcleo científico del subsistema 2. Implementa la psicometría oficial del Ministerio del Trabajo de Ecuador (MDT) para 58 ítems con escala Likert 1-4, baremos oficiales (Tablas 3 y 4 del PDF gubernamental), consistencia interna (Cronbach α, McDonald ω, Spearman-Brown para 2 ítems), análisis factorial exploratorio (AFE) y validación cruzada estratificada.
5. **`src/simulador_intervencion.py`**: Módulo que une la priorización local de dimensiones con tamaños de efecto de meta-análisis (Richardson & Rothstein, 2008, $d = 0.526$). **No está conectado a la interfaz web**, opera solo vía CLI.
6. **`dashboard/app.py`**: Orquestador visual en Streamlit. Conecta ambos subsistemas renderizando primero el pipeline de IBM HR / Attrition y, al final, una sección aditiva (`componente_perfiles_psicosociales`) con el subsistema psicométrico.
7. **`tests/`**: Suite exhaustiva de pruebas unitarias y de integración para psicometría, datos, simulador y componentes UI (201 tests).
8. **`Docker` y CI/CD**: `Dockerfile` parametriza un entorno de ejecución Debian con Python 3.11 para Streamlit en el puerto 8501. `.github/workflows/test.yml` ejecuta `pytest tests/ -v` en GitHub Actions sobre Python 3.11, 3.12 y 3.13 en cada push a `main`.

---

## 2. Coherencia Arquitectónica y Conceptual

### 2.1 El Conflicto de Identidad del Repositorio

El proyecto nació como una herramienta de People Analytics sobre **rotación voluntaria de empleados (Employee Attrition)** utilizando el dataset sintético/benchmark de **IBM HR Analytics (Kaggle)** y una aproximación ad-hoc al modelo Job Demands-Resources (JD-R). Posteriormente, el proyecto experimentó un pivote radical hacia la **evaluación psicométrica de riesgo psicosocial laboral bajo la normativa ecuatoriana (MDT, 58 ítems)**, incorporando turnos rotativos, protocolos LOPDP y un simulador de intervenciones organizacionales.

Sin embargo, **el pivote no reemplazó la base previa; se superpuso a ella**. Como resultado, el repositorio sufre de una severa disonancia cognitiva en código, documentación y UI.

### 2.2 Inventario Exhaustivo de Residuos y Enfoques Cruzados

| Ubicación | Elemento / Fragmento | Problema de Coherencia |
|---|---|---|
| `pyproject.toml` (Línea 8) | `description = "Sistema de Analitica Predictiva de Rotacion de Personal"` | Mantiene la definición del producto anterior (Rotación) e ignora por completo la psicometría del MDT. |
| `dashboard/app.py` (Líneas 29-30) | `st.title("🔎 Vigía RH — Analítica Predictiva de Rotación")`, `st.markdown("Sistema de análisis de riesgo de rotación de personal")` | La cabecera principal del producto sigue siendo 100% sobre rotación de personal IBM. |
| `dashboard/app.py` (Líneas 36-48) | Carga por defecto `cargar_datos()` que apunta a IBM HR | Si el usuario no carga nada, el dashboard arranca con el dataset de Kaggle de IBM. |
| `dashboard/app.py` (Líneas 60-80) | Métricas de renuncias, gráficas de horas extra vs rotación, índice JD-R, modelo RandomForest | El 75% del dashboard está dedicado exclusivamente a predecir renuncias en IBM HR. |
| `dashboard/app.py` (Línea 85) | `componente_perfiles_psicosociales(PROJECT_ROOT)` pegado al final como sección "aditiva" | El cuestionario MDT aparece al fondo como un apéndice aislado, sin conexión con los datos de arriba. |
| `src/dashboard/ui_components.py` (Líneas 88-92) | `st.file_uploader(...)` validando columnas con `validar_columnas()` | El uploader de la pantalla principal **solo acepta el esquema IBM HR**. Si un usuario sube respuestas del cuestionario MDT, el sistema arroja `ValueError`. |
| `src/datos.py` (Líneas 16-18) | `RUTA_DATOS_DEFAULT = ... / "WA_Fn-UseC_-HR-Employee-Attrition.csv"` | El núcleo de datos del proyecto sigue fijado al archivo CSV de Kaggle. |
| `src/datos.py` (Líneas 21-30, 95) | `COLUMNAS_REQUERIDAS = ["Attrition", "OverTime", ...]` | Obliga a que cualquier dato entrante cumpla el esquema de IBM HR Analytics. |
| `src/datos.py` (Líneas 168-186) | `agregar_indice_compuesto_jdr()` | Calcula un índice inventado `(OverTime*2 + (5-JobSat) + ...)` que no guarda relación con la psicometría oficial. |
| `src/modelo.py` (Completo) | `RandomForestClassifier` prediciendo `Attrition` en IBM HR | Módulo dedicado a la predicción de renuncia individual sobre el dataset de IBM. |
| `src/explicabilidad.py` (Completo) | SHAP sobre variables de IBM (`MonthlyIncome`, `Age`, etc.) | Enfocado únicamente en el modelo de Attrition. |
| `src/reportes.py` (Completo) | `reporte_vigia_rh.pdf` (resumen de rotación, JD-R y SHAP) | Generador de PDF que ignora por completo la psicometría y el cuestionario MDT. |
| `src/marco_psicologico.py` (Completo) | `df.groupby("Attrition")["indice_compuesto_jdr"].mean()` | Compara el índice proxy con la rotación observada en IBM. |
| `data/RH_Empresa_Ejemplo_Ecuador.xlsx` | 10 filas con columnas traducidas de IBM HR | Archivo que simula una empresa ecuatoriana pero con los campos de IBM HR, no con los ítems del MDT. |
| `output/` (Varios archivos) | `modelo_vigia.joblib`, `shap_resumen.png`, `grafica1..3.html` | Artefactos generados a partir de IBM HR que consumen espacio en git. |
| `src/psicometria/__init__.py` (Línea 7) | `"...o del subset COPSOQ anterior."` | Residuo histórico de una versión intermedia (COPSOQ) previa al pivote al MDT. |
| `README.md` (Líneas 1-3, 35-63) | Título, justificación económica de rotación de personal (Gallup/SHRM) y fórmula JD-R | El README vende un sistema de predicción de rotación en sus primeros capítulos. |
| `README.md` (Línea 79) | `"Sección Perfiles Psicosociales: vía validada basada en COPSOQ"` | **Contradicción flagrante en el README:** afirma usar COPSOQ cuando todo el módulo usa el cuestionario MDT (58 ítems). |
| `README.md` (Línea 372) | `"Fase 8: instrumento COPSOQ, fiabilidad, AFE..."` | Registra en el Roadmap el uso de COPSOQ. |
| `README.md` (Líneas 108-126, 222-237) | Diagrama Mermaid de Arquitectura | El diagrama de arquitectura oficial del README **no incluye `src/psicometria/` ni `src/simulador_intervencion.py`**. Solo dibuja el flujo de IBM HR. |
| `src/simulador_intervencion.py` | Desconectado de la interfaz gráfica | No existe ninguna pantalla ni botón en Streamlit para interactuar con este simulador. |

---

## 3. Estado Real del Modelo Predictivo

### 3.1 Diagnóstico Técnico

La pregunta clave de auditoría es: **¿El dashboard realiza inferencia real en caliente con un modelo serializado, o únicamente despliega gráficos estáticos precomputados?**

**Respuesta concluyente:** El dashboard implementa **AMBOS patrones de forma simultánea**, con una notable inconsistencia técnica y un bug funcional de indexación.

### 3.2 Evidencia Línea por Línea

#### A. Evidencia de Resultados Precomputados (Imágenes Estáticas)
En `src/dashboard/ui_components.py`, líneas 295 a 316:
```python
# Archivo: src/dashboard/ui_components.py, Líneas 304-308
st.subheader("Explicabilidad del modelo (SHAP)")
shap_path = project_root / "output" / "shap_resumen.png"

if shap_path.exists():
    st.image(str(shap_path), caption="Variables que más influyen en la rotación, según SHAP")
```
- **Hallazgo:** La sección general de explicabilidad SHAP **no calcula nada en vivo**. Lee directamente del disco el archivo PNG `output/shap_resumen.png` generado previamente por `src/explicabilidad.py`. Si ese archivo se borra, muestra un mensaje estático indicando que no existe.

#### B. Evidencia de Inferencia Real en Caliente con Modelo Serializado
En `src/dashboard/ui_components.py`, líneas 355 a 444 (`componente_modelo_prediccion`):
```python
# Archivo: src/dashboard/ui_components.py, Líneas 369-376
modelo_path = project_root / "output" / "modelo_vigia.joblib"
modelo = _cargar_modelo_cacheado(str(modelo_path)) # Ejecuta joblib.load(ruta)

# Archivo: src/dashboard/ui_components.py, Líneas 380-383
df, X_test, y_test = _cargar_datos_preparados() # Lee CSV y corre train_test_split en vivo
métricas = _calcular_metricas_cacheadas(modelo, X_test, y_test) # Ejecuta modelo.predict()

# Archivo: src/dashboard/ui_components.py, Líneas 405-406
predicción = modelo.predict(empleado_features)[0] # <── INFERENCIA REAL EN VIVO
probabilidad = modelo.predict_proba(empleado_features)[0] # <── PROBABILIDAD REAL EN VIVO

# Archivo: src/dashboard/ui_components.py, Líneas 350-352 y 417
# En _calcular_shap_cacheado:
explicador = shap.TreeExplainer(_modelo)
return explicador(X_test) # <── CÁLCULO SHAP DINÁMICO EN VIVO
shap_values = _calcular_shap_cacheado(modelo, X_test)

# Archivo: src/dashboard/ui_components.py, Líneas 431-441
fig, ax = plt.subplots(figsize=(10, 6))
# ... dibuja barras horizontales con matplotlib y las manda a Streamlit:
st.pyplot(fig) # <── RENDERIZADO DINÁMICO
```
- **Hallazgo:** El componente carga efectivamente el archivo `.joblib` en memoria usando `@st.cache_resource`, ejecuta predicciones en tiempo real sobre las features del empleado seleccionado, corre `shap.TreeExplainer` sobre el split de test y dibuja un gráfico de barras interactivo con Matplotlib.

#### C. Bug Crítico de Indexación en la Inferencia en Vivo
En `src/dashboard/ui_components.py`, líneas 398 a 405:
```python
# Línea 402: crea un selectbox con el rango del DataFrame completo (1470 filas)
idx_empleado = st.selectbox("Seleccionar empleado:", range(len(df)))

# Línea 404: intenta indexar X_test (que solo tiene el 20% del split = 294 filas)
empleado_features = X_test.iloc[[idx_empleado]]
```
- **Fallo identificado:** `len(df)` es 1470, pero `len(X_test)` es 294. Si el usuario selecciona en la interfaz cualquier empleado con índice $\ge 294$, Streamlit captura una excepción `IndexError: single positional indexer is out-of-bounds`.
- **Desalineación de datos:** Incluso para índices $< 294$, la posición `i` en `df` no coincide con la posición `i` en `X_test` (dado que `train_test_split` baraja aleatoriamente los índices con `random_state=42`). La predicción mostrada corresponde a una persona distinta a la seleccionada en el menú.

#### D. Estado del Subsistema Psicométrico (MDT)
En `src/psicometria/vista_dashboard.py`, líneas 230 a 285:
- **No existe ningún modelo serializado de Machine Learning.**
- Todos los cálculos son **estadísticos y psicométricos en caliente**: cálculo de sumatorias simples según baremos del MDT, consistencia interna (fórmulas de NumPy para $\alpha$, $\omega$ y Spearman-Brown), descomposición en autovalores (`np.linalg.eigh`) para el análisis factorial exploratorio y correlaciones de Pearson en vivo (`np.corrcoef`).

---

## 4. Salud Técnica del Repositorio

### 4.1 Imports y Dependencias
- **Imports rotos:** No se registran fallos de sintaxis ni `ImportError` al importar los módulos de `src` desde la raíz.
- **Dependencias en `requirements.txt`:** Todas las dependencias importadas en código (`fpdf2`, `joblib`, `matplotlib`, `numpy`, `openpyxl`, `pandas`, `plotly`, `psutil`, `pytest`, `scikit-learn`, `shap`, `streamlit`) están formalmente declaradas en `requirements.txt`.
- **Omisión de herramientas de desarrollo:** No existen secciones para dependencias de desarrollo (linters, formatters, type-checkers como `ruff`, `black`, `mypy`).

### 4.2 Código Duplicado

Se identificaron cuatro bloques de duplicación flagrante:
1. **Preprocesamiento y codificación categórica:**
   El bloque que itera sobre columnas `object`, aplica `.astype("category").cat.codes`, elimina `Attrition` y corre `train_test_split(..., test_size=0.2, random_state=42)` está idéntico en tres archivos distintos:
   - `src/modelo.py` (Líneas 26-36)
   - `src/explicabilidad.py` (Líneas 26-36)
   - `src/dashboard/ui_components.py` (Líneas 322-330)
2. **Distribución y conteo de niveles de riesgo:**
   La función que cuenta respondientes en niveles Bajo/Medio/Alto está duplicada con ligeras variantes en:
   - `src/simulador_intervencion.py` (Líneas 92-98, `_distribucion`)
   - `src/psicometria/reporte.py` (Líneas 67-77, `_distribucion_riesgo`)
3. **Reconfiguración UTF-8 de streams en consolas Windows:**
   El bucle `for stream in (sys.stdout, sys.stderr): stream.reconfigure(...)` está duplicado exactamente en:
   - `src/psicometria/cli.py` (Líneas 23-27)
   - `src/simulador_intervencion.py` (Líneas 320-324)
4. **Manipulación de `sys.path` mediante `PROJECT_ROOT`:**
   El patrón `PROJECT_ROOT = Path.cwd(); if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0, ...)` se repite en 8 archivos distintos (`app.py`, `modelo.py`, `explicabilidad.py`, `reportes.py`, `marco_psicologico.py`, `simulador_intervencion.py`, `vista_dashboard.py`, `cli.py`).

### 4.3 Archivos Muertos y Huérfanos

1. **`src/explicabilidad.py`:** Módulo huérfano. Ningún archivo en `src/`, `dashboard/` o `tests/` importa sus funciones (`generar_explicacion_empleado`, `generar_grafica_shap`, `obtener_top_variables`). El dashboard implementó su propio código de SHAP directamente en `ui_components.py`.
2. **`notebooks/explorar.py` y `notebooks/graficas.py`:** Scripts abandonados sin guards `if __name__ == "__main__"`. Al ejecutarse desde la raíz arrojan `FileNotFoundError: '../data/WA_Fn-UseC_-HR-Employee-Attrition.csv'` debido a rutas relativas no resueltas.
3. **`output/grafica1_horas_extra.html`, `grafica2_departamento.html`, `grafica3_satisfaccion.html`:** Tres archivos generados por `notebooks/graficas.py` que pesan **4.3 MB cada uno (13 MB en total)**. Están comiteados en git pero ningún módulo ni el dashboard los lee jamás.
4. **`data/RH_Empresa_Ejemplo_Ecuador.xlsx`:** Archivo de 10 filas ignorado por `.gitignore` pero presente en el workspace local; no participa en tests ni en el pipeline activo.

### 4.4 Rutas Relativas Frágiles

Existe un grave antipatrón en toda la base de código de producción: el uso indiscriminado de `Path.cwd()` y `os.getcwd()` en lugar de anclar las rutas a `Path(__file__).resolve().parent`:
- `src/datos.py:14-17`: `SRC_DIR = os.path.join(os.getcwd(), "src")`, `PROJECT_ROOT = os.getcwd()`
- `src/modelo.py:4`: `PROJECT_ROOT = Path.cwd()`
- `src/explicabilidad.py:4`: `PROJECT_ROOT = Path.cwd()`
- `src/reportes.py:6`: `PROJECT_ROOT = Path.cwd()`
- `src/marco_psicologico.py:4`: `PROJECT_ROOT = Path.cwd()`
- `src/simulador_intervencion.py:50`: `PROJECT_ROOT = Path.cwd()`
- `src/psicometria/vista_dashboard.py:17`: `PROJECT_ROOT = Path.cwd()`
- `src/utils/logger.py:44`: `logs_dir = Path.cwd() / "logs"`
- `dashboard/app.py:5`: `PROJECT_ROOT = Path.cwd()`

**Impacto:** Si un script, una tarea de cron o un subproceso se invoca desde cualquier directorio que no sea la raíz del repositorio (por ejemplo, ejecutando `python c:\Users\User\vigia-rh\src\modelo.py` estando posicionado en `C:\Users\User`), `Path.cwd()` resuelve a ese directorio ajeno, `sys.path.insert(0, ...)` inyecta una ruta errónea, y la ejecución colapsa con `ModuleNotFoundError: No module named 'src'`. En contraste, los archivos de pruebas en `tests/` (`conftest.py` y `test_dashboard.py`) sí utilizan adecuadamente `Path(__file__).resolve().parent.parent`.

### 4.5 Resultado de los Tests

Al ejecutar `pytest -v` en el entorno virtual:
```
============================ 201 passed in 45.02s =============================
```
- **Pruebas que pasan:**
  - `tests/test_calidad_datos.py`: 18 tests (rango 1-4, faltantes, duplicados, varianza cero).
  - `tests/test_datos.py`: 29 tests (lectura CSV/Excel, validación de columnas, normalización booleana, fórmula JD-R).
  - `tests/test_dashboard.py`: 55 tests (detección de formato, validaciones de archivo, mocks de Streamlit para métricas, gráficos JD-R y SHAP estático).
  - `tests/test_psicometria.py`: 56 tests (baremos oficiales, consistencia interna $\alpha$, $\omega$, Spearman-Brown, AFE, validez de criterio, simulación de N).
  - `tests/test_psicometria_cli.py`: 28 tests (reportes en texto, PDF, CLI, plantilla de respuestas).
  - `tests/test_simulador_intervencion.py`: 16 tests (catálogo de intervenciones, priorización de correlaciones, cálculos de desplazamientos).
  - `tests/test_vista_dashboard.py`: 11 tests (renderizado de componentes psicométricos en Streamlit).

- **Brechas Críticas de Cobertura (Código sin ningún test):**
  - **`src/modelo.py`**: **0 tests**. No hay pruebas unitarias para `entrenar_modelo`, `evaluar_modelo`, `guardar_modelo` ni `cargar_modelo`.
  - **`src/explicabilidad.py`**: **0 tests**.
  - **`src/reportes.py`**: **0 tests**.
  - **`src/marco_psicologico.py`**: **0 tests**.
  - **`src/dashboard/ui_components.py::componente_modelo_prediccion`**: **0 tests** (por esta razón el bug de indexación pasó completamente desapercibido en el pipeline de CI).
  - **`start_dashboard_safe.py`**: **0 tests**.

---

## 5. Lenguaje Ético y Científico

### 5.1 Instrumentos "Validados" sin Serlo
1. **Residuos de COPSOQ en documentación:**
   - En `README.md` (Línea 79): *"Sección Perfiles Psicosociales: vía validada basada en COPSOQ"*.
   - En `README.md` (Línea 372): *"Vía psicométrica validada (src/psicometria): instrumento COPSOQ..."*.
   - **Crítica:** COPSOQ no está implementado en el código actual; fue reemplazado por el cuestionario del MDT. Presentar un subset no validado empíricamente en la empresa como "vía validada" induce a engaño metodológico.
2. **Confusión entre validación nacional y validez local:**
   - En `src/psicometria/instrumento.py` (Líneas 48-54) y en reportes generados se citan los coeficientes alfa de la Universidad Central del Ecuador y la Universidad Internacional SEK ($\alpha = 0.967$, muestra nacional $n=4346$).
   - Aunque el código aclara en comentarios que corresponden a la validación nacional, los reportes al usuario tienden a mezclar la fiabilidad nacional del instrumento con la fiabilidad de la muestra propia de la empresa evaluada.

### 5.2 Afirmaciones Causales no Justificadas
1. **"Impacto" del Simulador de Intervención:**
   - `src/simulador_intervencion.py` modela intervenciones aplicando una reducción fija de desviación estándar ($d = 0.526$) proveniente de un meta-análisis de 2008 (Richardson & Rothstein) a los datos locales para estimar cuántos empleados "salen de riesgo Alto".
   - **Riesgo:** Aunque el código incorpora advertencias explícitas en el texto (`caveats`), la presentación cuantitativa de personas que "salen de riesgo alto" frente a comités de dirección o RRHH induce a asumir causalidad directa y retornos de inversión garantizados, omitiendo factores de confusión contextuales.
2. **Causalidad espuria en correlaciones y SHAP:**
   - En `src/marco_psicologico.py` (Líneas 24-25): *"Esto muestra si nuestra lectura conceptual del JD-R coincide con lo que el modelo predictivo encontró por su cuenta"*. Un modelo asociativo de Random Forest no valida la teoría del JD-R; únicamente detecta correlaciones en un dataset de juguete.
   - En `src/dashboard/ui_components.py` (Línea 426): *"Mayor riesgo de rotación / Menor riesgo de rotación"* atribuido a las magnitudes SHAP, sugiriendo erróneamente que modificar esa variable reducirá linealmente la rotación.

### 5.3 Exposición Indebida de Datos Individuales de Empleados
1. **Vulneración directa del compromiso ético en el dashboard:**
   - En `src/dashboard/ui_components.py` (Líneas 397-414), el componente `componente_modelo_prediccion` presenta:
     - Un selector interactivo por empleado individual: `Empleado #{i} (Dept: Sales, Age: 41)`.
     - Una predicción binaria individual: `Predicción del Modelo: Rotación (Sí)`.
     - Probabilidad estimada de renuncia: `Prob. rotación: 78.4%`.
     - Desglose SHAP de los factores personales que empujan a esa persona a renunciar.
2. **Contradicción con la política de privacidad y LOPDP del proyecto:**
   - `docs/CONSENTIMIENTO.md` (Líneas 49-50) estipula terminantemente: *"Los resultados se reportan solo a nivel grupal... nunca de manera individual"*.
   - `docs/PROTOCOLO_SITUACIONES_DETECTADAS.md` (Líneas 15-18) prohíbe explícitamente cualquier análisis individual o desgloses en grupos menores a 5 personas para evitar reidentificación.
   - `README.md` (Línea 23) declara: *"El código no debe usarse para tomar decisiones individuales sobre contratación, despido, ascenso o sanción de personas"*.
   - **Dictamen:** Mantener una pantalla interactiva que señala individualmente qué empleado va a renunciar viola flagrantemente el marco ético defendido en el propio repositorio, convirtiendo el proyecto en una herramienta susceptible de persecución laboral o perfilamiento no consentido.

---

## 6. Interfaz e Imagen del Producto

### 6.1 Jerarquía Visual y Navegación
- **Falta de modularidad en la vista:** `dashboard/app.py` presenta un scroll vertical interminable de 94 líneas donde se apilan 8 secciones separadas únicamente por `st.divider()`.
- **Ausencia de navegación:** No se utilizan componentes modernos de Streamlit como pestañas (`st.tabs`), menús laterales (`st.sidebar`) o páginas múltiples (`pages/`).
- **Coexistencia forzada:** Un directivo de RRHH que ingresa al sistema observa métricas globales de rotación financiera en la cabecera, gráficos exploratorios en el medio, un predictor de despidos individuales más abajo, y tablas estadísticas densas del Ministerio de Trabajo al final. No hay una narrativa visual coherente.

### 6.2 Consistencia de Colores y Tipografía
- **Inconsistencia de paletas:** No existe configuración de tema (`theme`) en `.streamlit/config.toml`. La aplicación depende del tema claro/oscuro que tenga el navegador del cliente.
- **Colores inaccesibles (daltonismo):** En `src/dashboard/ui_components.py` (Línea 433), el gráfico de barras Matplotlib asigna colores fijos mediante `colores = ["red" if v > 0 else "green" for v in top_features.values]`. Esta combinación rojo/verde viola pautas de accesibilidad visual (WCAG 2.1) y desentona con los gráficos vectoriales nativos de Plotly.

### 6.3 Textos y Claridad para el Usuario
- **Uploader engañoso:** El uploader de la cabecera (`componente_carga_archivo`) dice: *"Sube tu archivo (CSV, Excel) - opcional"*, pero solo procesa esquemas tipo IBM HR. Si se sube una encuesta del MDT, el sistema falla con error rojo en pantalla. Para cargar encuestas reales del MDT, el usuario debe copiar manualmente el archivo en el sistema de archivos del servidor bajo `data/encuestas/`, lo cual es inoperante para un usuario no técnico.
- **Densidad matemática no traducida:** En la sección psicométrica, la interfaz arroja siglas crudas como `SB=0.85`, `α=0.88`, `ω=0.91` o tablas de cargas factoriales `F1 / F2` sin una interpretación ejecutiva orientada al bienestar de los trabajadores.

### 6.4 Calidad del README como Caso de Estudio
- **Placeholder descuidado:** En la línea 31 de `README.md`, permanece visible el texto instructivo sin completar:
  ```markdown
  > *(Reemplazar esta línea por una screenshot real 1200x700 del dashboard corriendo localmente: métricas + histograma JD-R + disclaimer st.warning() + imagen SHAP)*
  ```
- **Datos de contacto sin rellenar:** En las líneas 394-396 de `README.md`:
  ```markdown
  - 🔗 LinkedIn: *(agrega tu link)*
  - 🐙 GitHub: *(agrega tu link)*
  - ✉️ Email: *(agrega tu correo profesional)*
  ```
- **Referencia a archivo inexistente:** En la línea 383 se cita `(ver archivo LICENSE)`, pero el archivo `LICENSE` no existe en la raíz del repositorio.
- **Falta de activos visuales:** No hay una sola captura de pantalla, diagrama vectorial exportado ni GIF demostrativo en todo el proyecto.

---

## 7. Calidad de Ingeniería de Software (Diagnóstico Técnico)

### 7.1 Métricas de Código (Type Hints y Docstrings)

El análisis estático mediante árbol de sintaxis abstracta (`ast`) sobre el repositorio arroja las siguientes métricas exactas:

| Ámbito | Funciones Totales | Con Docstrings | % Docstrings | Con Type Hints | % Type Hints |
|---|---|---|---|---|---|
| **Código de producción (`src/`)** | 99 | 96 | **97.0%** | 80 | **80.8%** |
| **Suite de pruebas (`tests/`)** | 215 | 207 | **96.3%** | 0 | **0.0%** |
| **Scripts auxiliares / arranque** | 3 | 3 | **100.0%** | 0 | **0.0%** |
| **TOTAL REPOSITORIO** | 317 | 306 | **96.5%** | 80 | **25.2%** |

- **Diagnóstico:** El subsistema `src/psicometria/` tiene un estándar sobresaliente (cercano al 100% de docstrings y type hints completos). En contraste, los módulos del subsistema anterior carecen totalmente de type hints:
  - `src/modelo.py`: 0 de 5 funciones tienen type hints (0%).
  - `src/explicabilidad.py`: 0 de 4 funciones tienen type hints (0%).
  - `start_dashboard_safe.py`: 0 de 3 funciones tienen type hints (0%).
  - `src/datos.py`: 3 funciones carecen de type hints (`renombrar_columnas_es`, `detectar_mapeo_propuesto`, `mostrar_mapeo_propuesto`).

### 7.2 Usos de `print()` vs. `logging`

Se detectaron **62 llamadas a `print()`** en archivos Python:
- **`start_dashboard_safe.py` (28 llamadas):** Utiliza `print()` para todo el ciclo de vida del proceso en lugar de registrar eventos en un logger.
- **`src/modelo.py` (8 llamadas):** Imprime métricas y reportes de clasificación en stdout dentro del bloque `if __name__ == "__main__"`.
- **`src/marco_psicologico.py` (4 llamadas):** Imprime comparaciones de medias en stdout dentro de la función de negocio `_analisis_conceptual()`.
- **`src/explicabilidad.py` (3 llamadas):** Imprime en el bloque principal.
- **`src/reportes.py` (1 llamada):** Imprime la ruta de salida.
- **`notebooks/` (6 llamadas):** Scripts interactivos.
- **`src/psicometria/cli.py` (10 llamadas) y `src/simulador_intervencion.py` (2 llamadas):** Justificadas por ser puntos de entrada CLI que formatean la salida para el usuario.

### 7.3 Bloques `except` Genéricos y Antipatrones `pass`

Se contabilizaron **18 bloques `except Exception:`** y **7 bloques `pass`**:
1. **Tragado silencioso de errores en dashboard (`src/psicometria/vista_dashboard.py`, Líneas 325-329):**
   ```python
   except Exception as e:
       try:
           st.error(f"❌ Error en perfiles psicosociales: {e}")
       except Exception:
           pass  # <── TRAGADO SILENCIOSO DOBLE
       logger.error(...)
   ```
2. **Tragado en carga de encuestas (`src/psicometria/vista_dashboard.py`, Línea 151):**
   ```python
   try:
       df = pd.read_csv(archivo)
   except Exception:
       continue  # Omite silenciosamente archivos CSV corruptos sin avisar en UI ni log
   ```
3. **Bloques genéricos en componentes UI (`src/dashboard/ui_components.py`):**
   Las funciones `componente_metricas_principales`, `componente_filtro_departamento`, `componente_graficas_rotacion`, `componente_indice_jdr`, `componente_explicabilidad_shap` y `componente_modelo_prediccion` envuelven toda su lógica en `except Exception as e:`. Aunque evita que la aplicación web colapse ante fallos menores, oculta bugs de desarrollo críticos (como el `IndexError` documentado en la Sección 3).
4. **Instalación dinámica no controlada en runtime (`start_dashboard_safe.py`, Líneas 120-125):**
   ```python
   try:
       import psutil
   except ImportError:
       subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
       import psutil
   ```
   Invocar `pip install` al importar un script de monitoreo es un antipatrón severo que compromete la predictibilidad de entornos productivos.

### 7.4 Configuración de Ruff / Black y Cumplimiento de Estilo

- **Configuración existente:** **No existe ninguna configuración** para `ruff`, `black`, `flake8` ni `isort` en `pyproject.toml`, ni en archivos dedicados (`.ruff.toml`, `setup.cfg`).
- **Cumplimiento actual de estándares:**
  - **224 líneas** superan el límite de 88 caracteres exigido por Black.
  - **111 líneas** superan los 100 caracteres.
  - **48 líneas** superan los 120 caracteres.
  - **94 líneas** contienen espacios en blanco redundantes al final (*trailing whitespace*).
  - El archivo `tests/test_calidad_datos.py` contiene un carácter no imprimible BOM UTF-8 (`\ufeff`) en su primera línea.

---

### 7.5 Diagnóstico de Refactorización y Evaluación de Riesgo

A continuación se diagnostica cada anomalía de ingeniería, evaluando si amerita refactorización y estimando el riesgo de regresión sobre la suite de pruebas existente:

| Hallazgo / Oportunidad de Refactorización | ¿Vale la pena refactorizar? | Nivel de Riesgo para Tests | Evaluación de Riesgo / Retorno y Justificación Técnica |
|---|---|---|---|
| **Separar la lógica de negocio y ETL de la interfaz en `ui_components.py` y resolver el bug de indexación** | **SÍ (Urgente)** | **Bajo** | **Retorno muy alto.** `componente_modelo_prediccion` tiene 0 pruebas en pytest, por lo que refactorizar su interior no romperá la suite actual. Corregirá la excepción `IndexError` y desacoplará el cálculo SHAP de la vista. |
| **Reemplazar rutas relativas frágiles (`Path.cwd()`) por `Path(__file__).resolve().parent...`** | **SÍ (Crítico)** | **Bajo** | **Retorno muy alto.** Garantiza la portabilidad del código desde cualquier directorio de trabajo o contenedor sin alterar la firma de ninguna función pública probada en los tests. |
| **Eliminar código duplicado de preprocesamiento entre `modelo.py`, `explicabilidad.py` y `ui_components.py`** | **SÍ** | **Bajo** | **Retorno medio.** Centralizar en `src/datos.py` una función `preparar_datos_modelo()` reduce deuda técnica. Como `modelo.py` y `explicabilidad.py` no tienen tests directos, el riesgo para la suite actual es nulo. |
| **Eliminar archivos muertos (`explicabilidad.py`, `notebooks/*.py`, `output/*.html`)** | **SÍ** | **Nulo** | **Retorno medio.** Reduce 13 MB de peso superfluo en el repositorio. Ningún test de la suite importa ni valida estos archivos. |
| **Eliminar la predicción individual de empleados (`Empleado #i`) por cumplimiento ético y LOPDP** | **SÍ (Ético)** | **Nulo** | **Retorno muy alto en reputación y cumplimiento legal.** Elimina la violación ética de exponer probabilidades individuales de renuncia. No hay tests cubriendo esa sección en `test_dashboard.py`. |
| **Incorporar `src/simulador_intervencion.py` al dashboard mediante una pestaña dedicada en Streamlit** | **SÍ** | **Bajo** | **Retorno alto.** Integra el simulador de impacto en la interfaz web. Sus cálculos están cubiertos al 100% por `test_simulador_intervencion.py` (16 tests), los cuales no se verían afectados al importar la función en la vista. |
| **Añadir Type Hints en `src/modelo.py` y `src/datos.py`** | **SÍ** | **Nulo** | **Retorno medio.** Los type hints son puramente informativos para análisis estático y no modifican el comportamiento en tiempo de ejecución de Python ni alteran las pruebas. |
| **Configurar e introducir Ruff y Black en `pyproject.toml` y CI** | **SÍ** | **Bajo** | **Retorno alto.** Formatea automáticamente las 224 líneas que exceden 88 caracteres y elimina trailing whitespaces. Debe cuidarse únicamente la sintaxis en archivos con strings multilínea de baremos. |
| **Desacoplar el diccionario de 58 ítems en `src/psicometria/instrumento.py` a JSON/YAML** | **NO** | **Alto** | **Riesgo innecesario.** Mover `ITEMS` y `PUNTOS_CORTE` a un archivo externo introduce riesgo de I/O en empaquetado y rompería directamente decenas de aserciones en `tests/test_psicometria.py` que importan las constantes como diccionarios nativos. |
| **Refactorizar `src/psicometria/reporte.py` separando el motor FPDF2 a un submódulo** | **OPCIONAL** | **Medio** | **Retorno bajo a corto plazo.** Funciona de forma estable y cuenta con cobertura integral en `tests/test_psicometria_cli.py`. Modificar la estructura de clases de FPDF2 podría generar regresiones en formato PDF sin aportar valor inmediato al usuario. |

---

## 8. Conclusión Ejecutiva

El repositorio **Vigía RH** exhibe un trabajo técnico y científico de gran valor en su subsistema psicométrico (`src/psicometria/`), respaldado por una batería impecable de 201 pruebas unitarias, apego fidedigno a la norma oficial ecuatoriana del MDT y un desarrollo riguroso de indicadores estadísticos en NumPy puro.

Sin embargo, el proyecto presenta una **crisis de identidad arquitectónica no resuelta**:
1. Conserva la fachada completa de un proyecto anterior de Machine Learning sobre rotación de personal (IBM HR) que monopoliza la cabecera del dashboard, el README y la entrada de datos.
2. Contiene una funcionalidad en el dashboard de predicción individual por empleado que **contradice frontalmente su propio protocolo ético y la LOPDP**.
3. Mantiene archivos huérfanos de gran volumen y rutas relativas dependientes de `cwd` que comprometen la solidez en despliegue.

Completar formalmente la transición hacia la analítica ética de factores psicosociales (unificando la entrada de datos alrededor del cuestionario MDT, eliminando el perfilamiento individual y limpiando los residuos de rotación e IBM HR) consolidará a Vigía RH como un referente técnico y metodológico de People Analytics en la región.
