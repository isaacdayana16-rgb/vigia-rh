# 🔎 Vigía RH — People Analytics Ético & Rotación Predictiva

> Intersección entre **Psicología Organizacional** (marco conceptual Job Demands-Resources) y **Ciencia de Datos** (Streamlit + pandas + Plotly + scikit-learn + SHAP).

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.63+-red?logo=streamlit)
![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas)
![Plotly](https://img.shields.io/badge/Plotly-Express-3F4F75?logo=plotly)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.9.0-FFCB2E?logo=scikit-learn)
![joblib](https://img.shields.io/badge/joblib-serialized_model-00B04A?logo=joblib)
![FPDF](https://img.shields.io/badge/FPDF2-reportes-EC1C24)
![License](https://img.shields.io/badge/Licencia-MIT-green)
![Status](https://img.shields.io/badge/Estado-Modelo%20predictivo%20funcional-green)

---

## ⚠️ Compromiso ético (léeme antes de usar)

Este proyecto es **estrictamente exploratorio** y no reemplaza la práctica profesional:

- ✅ El indicador principal se denomina **Índice compuesto JD-R (exploratorio)**, "inspirado conceptualmente" en el modelo Job Demands-Resources.
- ❌ **NO** es un instrumento psicométrico validado, **NO** es diagnóstico clínico, y **NO** evalúa síndrome de burnout, MBI, UWES-9 ni ningún test sancionado.
- 🧪 El dataset de demostración es **IBM HR Analytics Employee Attrition (dataset público de Kaggle)**: no contiene datos reales de empleados.
- 🚫 El código **no debe usarse** para tomar decisiones individuales sobre contratación, despido, ascenso o sanción de personas.

---

## 📸 Preview del dashboard

> *(Reemplazar esta línea por una screenshot real 1200x700 del dashboard corriendo localmente: métricas + histograma JD-R + disclaimer st.warning() + imagen SHAP)*

---

## 🎯 Contexto: el problema de la rotación

Reemplazar a un empleado cuesta, en promedio, entre 6 y 9 meses de su salario (estudios de SHRM y Gallup).
La mayoría de reportes de RRHH describen **qué** está pasando (kpis de rotación), pero no aportan un **marco conceptual** para entender **por qué** ni para priorizar acciones de mitigación.

Vigía RH cierra esa brecha traduciendo variables operativas de RRHH a la lente del **modelo Job Demands-Resources (JD-R, Bakker & Demerouti, 2007)**.

---

## 🧠 Marco conceptual JD-R (trasfondo del índice)

El modelo JD-R diferencia dos ejes que afectan el bienestar y la permanencia:

| Eje | Descripción | Representación en el índice |
|---|---|---|
| **Demandas** | Factores del trabajo que agotan energía (horas extra, carga mental) | Peso positivo: **Horas extra × 2** |
| **Recursos** | Factores que protegen y motivan (satisfacción, balance vida-trabajo, relación con el jefe) | Peso inverso: `(5 − Satisfacción) + (5 − Balance) + (5 − Relación)` |

**Fórmula publicada, 100% transparente** ([src/datos.py](file:///c:/Users/User/vigia-rh/src/datos.py#L77-L82)):
```
indice_compuesto_jdr =
    OverTime × 2
    + (5 − JobSatisfaction)
    + (5 − WorkLifeBalance)
    + (5 − RelationshipSatisfaction)
```

Rango teórico: **0 (menor desgaste)** → **14 (mayor desgaste)**. A mayor valor, perfil asociado estadísticamente a mayor rotación en el dataset demo.

---

## ✅ Qué hace HOY el producto (features reales, committeadas)

1. **🔌 Pipeline de datos centralizado** (`src/datos.py`):
    - Carga de CSV/Excel con ruta configurable.
    - Mapeo dinámico español-inglés para columnas en ambos idiomas.
    - `validar_columnas()`: validación estricta del esquema mínimo IBM HR (8 columnas).
    - `agregar_indice_compuesto_jdr(df)`: cálculo único del indicador (fuente de verdad).
2. **📊 Dashboard interactivo Streamlit** (`dashboard/app.py`):
    - 3 métricas de rotación globales.
    - Filtro dinámico por **Departamento**.
    - 2 histogramas Plotly (horas extra / satisfacción laboral) segmentados por Attrition.
    - **Sección Índice JD-R**: métrica promedio + histograma 0..14 + disclaimer ético `st.warning()`.
    - **Sección Modelo Predictivo**: métricas de performance (accuracy, precision, recall, F1), predicción por empleado seleccionable, y explicación SHAP dinámica por predicción individual.
3. **🤖 Modelo predictivo** (`src/modelo.py`):
     - RandomForestClassifier (scikit-learn) entrenado y serializado con joblib.
     - 5 funciones modulares: `entrenar_modelo()`, `evaluar_modelo()`, `guardar_modelo()`, `cargar_modelo()`, `obtener_importancias()`.
     - Accuracy: ~87.4% en dataset de prueba. Feature más importante: `MonthlyIncome`.
     - Documentación completa: [`docs/API_MODELO.md`](docs/API_MODELO.md).
4. **📄 Reporte PDF automatizado** (`src/reportes.py`):
    - Encabezado, resumen general, sección JD-R (con disclaimer), sección SHAP (con disclaimer).
5. **📘 Script de lectura conceptual** (`src/marco_psicologico.py`):
    - Compara promedio del índice JD-R entre empleados que renunciaron vs los que se quedaron (validación exploratoria del dataset demo).

---

## 🔄 Pipeline ETL y flujo de datos

### Flujo de datos

```
[Dataset IBM HR (CSV/Excel)]
         │
         ▼
┌─────────────────────────────┐
│  src/datos.py               │
│  1. cargar_datos()          │  ← Lee CSV/Excel, maneja encoding
│  2. validar_columnas()      │  ← Valida esquema mínimo (8 col)
│  3. renombrar_columnas_es() │  ← Mapeo ES→EN si aplica
│  4. agregar_indice_jdr()    │  ← Calcula índice compuesto JD-R
└─────────────────────────────┘
         │
         ├──► [dashboard/app.py]  ← Consume DataFrame, renderiza UI
         │
         ├──► [src/modelo.py]    ← Entrena RandomForestClassifier
         │                         → output/modelo_vigia.joblib
         │
         └──► [src/reportes.py]  ← Genera PDF con fpdf2
```

### Escalabilidad con datos reales

El pipeline está diseñado para escalar con datos reales de RRHH. Para ello:

1. **Carga**: `cargar_datos(ruta="...")` acepta cualquier ruta. Con datos reales, el archivo se coloca en `data/` o se pasa la ruta completa.
2. **Validación**: `validar_columnas()` garantiza que el esquema sea consistente antes de cualquier procesamiento. Si el schema cambia, el error es inmediato y explícito.
3. **Mapeo**: `renombrar_columnas_es()` detecta automáticamente columnas en español y las traduce al esquema interno en inglés. Con datos de diferentes fuentes, basta con actualizar `MAPEO_ES` en `src/datos.py`.
4. **Índice JD-R**: `agregar_indice_compuesto_jdr()` es la única fuente de verdad del cálculo del índice. Cualquier cambio en la fórmula se hace en un solo lugar.
5. **Modelo**: `entrenar_modelo()` recibe cualquier DataFrame con el esquema correcto. Para datos reales con más features, el modelo los incorpora automáticamente.

### Limitaciones actuales (honestidad técnica)

- **No hay data drift detection**: el modelo no detecta cambios en la distribución de datos a lo largo del tiempo.
- **No hay monitoreo de calidad de datos**: no hay alertas automáticas si los datos entrantes tienen anomalías.
- **No hay pipeline automatizado**: el entrenamiento se ejecuta manualmente con `python src/modelo.py`. Para automatizar, se necesita un orquestador (Airflow, Prefect, etc.) que no está implementado.
- **El dataset es de demo**: los resultados provienen del dataset público IBM HR Analytics de Kaggle, no de datos reales de empleados.

---

## 🧱 Stack tecnológico (al día con el código actual)

| Capa | Librería | Propósito |
|---|---|---|
| Lenguaje | Python 3.11+ | Runtime. |
| Dashboard | Streamlit | Interfaz web interactiva. |
| Datos | pandas | DataFrames y validación. |
| ML | scikit-learn | RandomForestClassifier, métricas. |
| Explicabilidad | SHAP | Explicación dinámica por predicción. |
| Serialización | joblib | Guardar/cargar modelo entrenado. |
| Viz | Plotly Express | Gráficas interactivas. |
| Reportes | fpdf2 | Exportación PDF. |
| Robustez imports | `pathlib` + `sys.path` idempotente | Funciona desde cualquier cwd. |

> Todas las dependencias están declaradas en `requirements.txt`. El modelo serializado (`output/modelo_vigia.joblib`) se genera ejecutando `python src/modelo.py`.

---

## 🏗️ Arquitectura modular

```mermaid
flowchart LR
    A[data/WA_Fn-UseC_-HR-Employee-Attrition.csv] --> B
    B[src/datos.py\n(carga + validacion + indice JD-R)]
    B --> C[dashboard/app.py\nUI interactiva Streamlit]
    B --> D[src/reportes.py\nreporte PDF]
    B --> E[src/marco_psicologico.py\nanalisis conceptual]
    B --> F[src/modelo.py\nentrenamiento + evaluacion]
    F --> G[output/modelo_vigia.joblib\nmodelo serializado]
    C --> H[src/modelo\ncargar_modelo + evaluar_modelo]
    H --> I[Explicacion SHAP dinamica\npor empleado]

    F --> I
    I --> C
    D --> J[output/reporte_vigia_rh.pdf]
```

**Diseño clave**: la fórmula del índice JD-R vive **en un solo lugar** (`src/datos.py`), y el modelo predictivo vive **en un solo módulo** (`src/modelo.py`). No existe duplicación en el repositorio.

---

## 🚀 Instalación y ejecución (100% reproducible)

### 1. Clonar y preparar entorno
```bash
git clone <URL_DE_TU_REPO>
cd vigia-rh

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```
Incluye: streamlit, pandas, plotly, fpdf2, openpyxl, scikit-learn, shap, matplotlib, psutil.

### 3. Generar el modelo predictivo (primera vez)
```bash
python src/modelo.py
# Genera output/modelo_vigia.joblib y muestra métricas.
# Solo necesario una vez; el dashboard usa el modelo serializado.
```

### 4. Ejecutar el dashboard
```bash
streamlit run dashboard/app.py
```
Abre `http://localhost:8501` en tu navegador.

### 5. (Opcional) Generar reporte PDF
```bash
python src/reportes.py
# Salida: output/reporte_vigia_rh.pdf
```

### 6. (Opcional) Análisis conceptual JD-R
```bash
python src/marco_psicologico.py
# Imprime en consola el promedio del índice por grupo de rotación.
```

---

## 📂 Estructura del proyecto

```
vigia-rh/
├── dashboard/
│   └── app.py                    # Entry point: UI Streamlit
├── data/
│   └── WA_Fn-UseC_-HR-Employee-Attrition.csv   # Dataset demo IBM
├── src/
│   ├── __init__.py               # Paquete Python
│   ├── datos.py                  # Núcleo: carga + validación + índice JD-R + mapeo ES-EN
│   ├── modelo.py                 # Modelo predictivo: entrenamiento, evaluación, serialización
│   ├── explicabilidad.py         # Explicabilidad SHAP por predicción
│   ├── reportes.py               # Generación PDF (FPDF2)
│   ├── marco_psicologico.py      # Lectura conceptual del índice
│   └── utils/
│       ├── logger.py             # VigiaLogger: logging estructurado
│       └── __init__.py
│   └── dashboard/
│       ├── __init__.py
│       ├── error_handler.py      # VigiaError, ErrorDatos, ErrorMapeo, ErrorCalculo
│       └── ui_components.py      # Componentes UI reutilizables + modelo predictivo
├── docs/
│   └── API_MODELO.md             # Documentación completa de la API del modelo
├── output/
│   ├── modelo_vigia.joblib       # Modelo predictivo serializado
│   ├── shap_resumen.png          # Plot SHAP precomputado
│   └── reporte_vigia_rh.pdf      # Último reporte generado
├── notebooks/                    # Análisis exploratorios (WIP)
├── requirements.txt
├── start_dashboard_safe.py       # Inicio seguro con monitoreo de procesos
└── README.md
```

---

## 📊 Hallazgos demo (del dataset IBM, no interpretables como "validación")

Al ejecutar `python src/marco_psicologico.py` se obtienen valores de promedio del **índice compuesto JD-R**:

| Grupo | Promedio JD-R (demo) |
|---|---|
| Empleados que **se quedaron** (Attrition = No) | `~7.18` |
| Empleados que **renunciaron** (Attrition = Yes) | `~8.35` |

> Aclaración: esta diferencia se observa **en este dataset demo puntual**. No constituye validación del modelo JD-R ni garantiza el mismo comportamiento en otra población.

---

## 🗺️ Roadmap (próximos pasos intencionales)

| Fase | Descripción | Estado |
|---|---|---|
| ✅ Fase 1 | Pipeline de datos, mapeo ES-EN, validación, dashboard descriptivo | **Completada** |
| ✅ Fase 2 | Modelo predictivo scikit-learn, serialización joblib, explicabilidad SHAP dinámica | **Completada** |
| 🔜 Fase 3 | Tests unitarios (`pytest`) sobre validación, índice JD-R y componentes de dashboard. | **Completada** |
| 🔜 Fase 4 | Dockerfile para despliegue reproducible. | **Completada** |
| 🔜 Fase 5 | GitHub Actions CI/CD pipeline. | **Completada** |
| 🔜 Fase 6 | Documentación de la API del modelo (`docs/API_MODELO.md`). | **Completada** |
| 🔜 Fase 7 | Documentación del pipeline ETL y escalabilidad. | **Completada** |
| 🔜 Fase 8 | Tests de integración para el dashboard completo. | **Pendiente** |
| 🔜 Fase 9 | Despliegue en Docker + Streamlit Cloud con CI/CD. | **Pendiente** |

---

## 📜 Licencia y créditos

- **Código**: Licencia MIT (ver archivo `LICENSE`).
- **Dataset demo**: IBM HR Analytics Employee Attrition & Performance, disponible públicamente en Kaggle.
- **Referencia conceptual**: modelo **JD-R** — *Bakker, A. B., & Demerouti, E. (2007). The job demands-resources model: State of the art.* Journal of Managerial Psychology.

---

## 👋 Autor / Contacto

**Isaac Reyes**
Psicología Organizacional · People Analytics · Data Science

- 🔗 LinkedIn: *(agrega tu link)*
- 🐙 GitHub: *(agrega tu link)*
- ✉️ Email: *(agrega tu correo profesional)*
